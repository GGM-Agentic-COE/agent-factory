import os
import json
import requests
from typing import Any, Type, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth


import boto3
from botocore.exceptions import ClientError


class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity. """
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    """
    AWSSecretReaderPodIdentity - Reads a AWS Secret using Pod Identity
    and returns the full key-value dict.
    """
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = "Reads a fixed AWS Secret (set in code) using Pod Identity, and returns all key-value pairs as a dict."
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    # Review every line tagged "SETUP-REQUIRED:" below before deploying this tool to a new environment or client.
    # SETUP-REQUIRED: must match the secret name created in your AWS Secrets Manager
    SECRET_NAME: str = "aava-secret-manager-jira-credentials"


    def _run(self) -> Dict[str, Any]:
        try:

            # SETUP-REQUIRED: AWS region where that secret lives (us-east-1 or us-east-2 depending on deployment)

            client = boto3.client('secretsmanager', region_name='us-east-1')
            get_secret_value_response = client.get_secret_value(SecretId=self.SECRET_NAME)
            secret_string = get_secret_value_response.get('SecretString', '{}')
            secret_dict = json.loads(secret_string)

            if not isinstance(secret_dict, dict):
                raise ValueError(f"Secret value is not a JSON object: {secret_dict}")

            return secret_dict

        except ClientError as e:
            raise RuntimeError(f"Error retrieving secret: {str(e)}")
        except Exception as ex:
            raise RuntimeError(f"Unexpected error: {str(ex)}")


reader = AWSSecretReaderPodIdentity()
secrets = reader._run()

# ============================================================================
# CONFIGURATION  --  edit these values for your Jira space (same as the creator)
# ============================================================================
JIRA_BASE_URL     = secrets.get("base_url")                     # from AWS Secrets Manager
JIRA_USER_EMAIL   = secrets.get("user_email")                   #from AWS Secrets Manager
JIRA_API_TOKEN    = secrets.get("api_token")                    #from AWS Secrets Manager
DEFAULT_MAX_DEPTH = 5            # how many levels of children to walk
PAGE_SIZE         = 100          # children fetched per page
# ============================================================================


class JiraIssueTreeFetcherSchema(BaseModel):
    """Input schema. Provide 'key' (str) or 'keys' (list); optional 'maxDepth',
    'includeChildren'. A JSON string or bare key string is coerced to a dict."""
    inputJSON: Dict[str, Any] = Field(
        ...,
        description=(
            "Dict with 'key' (e.g. 'GGMDEMOS-101') OR 'keys' (list of keys). "
            "Optional 'maxDepth' (default 5) and 'includeChildren' (default True)."
        ),
    )

    @field_validator("inputJSON", mode="before")
    @classmethod
    def _coerce_to_dict(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, list):
            return {"keys": v}
        if isinstance(v, str):
            s = v.strip()
            try:
                parsed = json.loads(s)
                if isinstance(parsed, dict):
                    return parsed
                if isinstance(parsed, list):
                    return {"keys": parsed}
                if isinstance(parsed, str):
                    s = parsed.strip()
            except (ValueError, TypeError):
                pass
            if "," in s:
                return {"keys": [k.strip() for k in s.split(",") if k.strip()]}
            return {"key": s}
        return v


class JiraIssueTreeFetcher(BaseTool):
    """Returns a clean, fixed-scheme JSON for a key/keys plus all nested child work items."""

    name: str = "Jira Issue Tree Fetcher"
    description: str = "Fetches title/status/description/labels/assignee/due date/reporter and nested children for a Jira key."
    args_schema: Type[BaseModel] = JiraIssueTreeFetcherSchema

    base_url: str = JIRA_BASE_URL

    # ----------------------------- ADF -> plain text -----------------------------
    def _adf_to_text(self, adf: Any) -> str:
        if adf is None:
            return ""
        if isinstance(adf, str):
            return adf
        if not isinstance(adf, dict):
            return str(adf)

        def render(node: dict) -> str:
            ntype = node.get("type")
            content = node.get("content", []) or []
            if ntype == "text":
                return node.get("text", "")
            if ntype == "hardBreak":
                return "\n"
            if ntype in ("paragraph", "heading"):
                return "".join(render(c) for c in content)
            if ntype == "bulletList":
                return "\n".join("- " + "".join(render(c) for c in li.get("content", [])).strip()
                                 for li in content)
            if ntype == "orderedList":
                return "\n".join(f"{i}. " + "".join(render(c) for c in li.get("content", [])).strip()
                                 for i, li in enumerate(content, 1))
            if ntype == "doc":
                return "\n".join(b for b in (render(c) for c in content) if b != "")
            return "".join(render(c) for c in content)

        return render(adf).strip()

    # ----------------------------- HTTP helpers -----------------------------
    def _get_issue(self, key: str) -> dict:
        url = f"{self.base_url}/rest/api/3/issue/{key}"
        r = requests.get(url, params={"fields": "*all"}, headers=self._headers, auth=self._auth)
        print("GET", key, "->", r.status_code)
        if not r.ok:
            return {"issue_id": key, "error": f"HTTP {r.status_code}", "detail": r.text}
        return r.json()

    def _get_children(self, key: str) -> List[dict]:
        url = f"{self.base_url}/rest/api/3/search/jql"
        jql = f'parent = "{key}" ORDER BY created ASC'
        out: List[dict] = []
        next_token: Optional[str] = None
        while True:
            body = {"jql": jql, "maxResults": PAGE_SIZE, "fields": ["*all"]}
            if next_token:
                body["nextPageToken"] = next_token
            r = requests.post(url, json=body, headers=self._headers, auth=self._auth)
            if not r.ok:
                break  # no children or not permitted; treat as leaf
            data = r.json()
            out.extend(data.get("issues", []))
            next_token = data.get("nextPageToken")
            if data.get("isLast", True) or not next_token:
                break
        return out

    # ----------------------------- scheme builder -----------------------------
    def _clean_node(self, raw: dict, child_nodes: List[dict]) -> dict:
        f = raw.get("fields", {}) or {}
        return {
            "issue_id": raw.get("key"),
            "title": f.get("summary", ""),
            "status": (f.get("status") or {}).get("name"),
            "description": self._adf_to_text(f.get("description")),
            "labels": f.get("labels", []) or [],
            "assignee": (f.get("assignee") or {}).get("displayName"),
            "due_date": f.get("duedate"),
            "reporter": (f.get("reporter") or {}).get("displayName"),
            "child_work_item_ids": [c.get("issue_id") for c in child_nodes],
            "children": child_nodes,
        }

    def _build_tree(self, raw: dict, depth: int) -> dict:
        key = raw.get("key")
        child_nodes: List[dict] = []
        if self._include_children and key and depth < self._max_depth and key not in self._visited:
            self._visited.add(key)
            for child_raw in self._get_children(key):
                child_nodes.append(self._build_tree(child_raw, depth + 1))
        return self._clean_node(raw, child_nodes)

    # ------------------------------- core -------------------------------
    def _run(self, inputJSON: Dict[str, Any]) -> str:
        try:
            self.base_url = (inputJSON.get("baseUrl") or self.base_url or JIRA_BASE_URL).rstrip("/")
            jira_user = inputJSON.get("userEmail") or JIRA_USER_EMAIL
            jira_token = inputJSON.get("apiToken") or JIRA_API_TOKEN or os.environ.get("JIRA_API_TOKEN", "")
            self._headers = {"Content-Type": "application/json", "Accept": "application/json"}
            self._auth = HTTPBasicAuth(jira_user, jira_token)
            self._max_depth = int(inputJSON.get("maxDepth") or DEFAULT_MAX_DEPTH)
            self._include_children = inputJSON.get("includeChildren", True)

            keys = inputJSON.get("keys")
            single = False
            if not keys:
                k = inputJSON.get("key")
                if not k:
                    return "Fatal error: provide 'key' (string) or 'keys' (list)."
                keys = [k]
                single = True
            if isinstance(keys, str):
                keys = [keys]

            trees = []
            for key in keys:
                self._visited = set()
                root = self._get_issue(key)
                if "error" in root:
                    trees.append(root)
                    continue
                trees.append(self._build_tree(root, 0))

            result = trees[0] if (single and len(trees) == 1) else trees
            return json.dumps(result, indent=2, ensure_ascii=False)

        except requests.RequestException as e:
            return f"Fatal error (network): {str(e)}"
        except Exception as e:
            return f"Fatal error: {str(e)}"


# Convenience wrapper for script / non-agent use
def fetch_issue_tree(keys, max_depth: int = DEFAULT_MAX_DEPTH, include_children: bool = True) -> str:
    payload = {"maxDepth": max_depth, "includeChildren": include_children}
    if isinstance(keys, (list, tuple)):
        payload["keys"] = list(keys)
    else:
        payload["key"] = keys
    return JiraIssueTreeFetcher()._run(payload)


if __name__ == "__main__":
    print(fetch_issue_tree("GGMDEMOS-101"))
