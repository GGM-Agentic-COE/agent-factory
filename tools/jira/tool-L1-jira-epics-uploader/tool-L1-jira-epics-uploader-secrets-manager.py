import os
import re
import json
import requests
from typing import Any, Type, Dict, List, Optional
from pydantic import BaseModel, Field
from requests.auth import HTTPBasicAuth

try:
    from crewai.tools import BaseTool  # type: ignore
    _CREWAI_AVAILABLE = True
except Exception:  # allow standalone use without crewai installed
    _CREWAI_AVAILABLE = False

    class BaseTool:  # minimal shim so the class still works standalone
        name: str = ""
        description: str = ""
        args_schema: Any = None

        def run(self, *args, **kwargs):
            return self._run(*args, **kwargs)



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
# CONFIGURATION  --  edit these four (five) values for your Jira space
# ============================================================================
JIRA_BASE_URL     = secrets.get("base_url")                      # from AWS Secrets Manager
JIRA_USER_EMAIL   = secrets.get("user_email")                    #from AWS Secrets Manager
JIRA_API_TOKEN    = secrets.get("api_token")                     #from AWS Secrets Manager
DEFAULT_ISSUE_TYPE = "Epic"                                      # used if none given

# If your project's issue-type scheme doesn't include "Epic"/"Story", Jira returns a
# MISLEADING "target project doesn't exist or you don't have permission" 400. Map the
# payload's types to whatever the project actually offers (see `python jira_preflight.py`).
# Example for a project that only has Task:  {"Epic": "Task", "Story": "Task"}
# Leave empty {} to send types through unchanged.
ISSUE_TYPE_MAP = {}                                              # e.g. {"Epic": "Task", "Story": "Task"}
# ============================================================================


# Matches the logical ids we use as labels: EP-01, F-01.2, FR-12, NFR-03, S1, etc.
_TOKEN_RE = re.compile(r'(?:EP|F|FR|NFR)-\d+(?:\.\d+)*')


class JiraIssueCreatorSchema(BaseModel):
    """Input schema for JiraIssueCreator."""
    inputJSON: Dict[str, Any] = Field(
        ...,
        description=(
            "A dictionary containing Jira issue creation parameters. May include "
            "'projectKey' (defaults to the hard-coded JIRA_PROJECT_KEY), 'issueType' "
            "(default issue type), and 'issues' (list of issue dicts with 'summary', "
            "'description', optional 'issueType', optional 'label', and optional "
            "'parentKey'). parentKey may be a logical id (e.g. 'EP-01') that is "
            "resolved to the real Jira key once the parent has been created."
        ),
    )


class JiraIssueCreator(BaseTool):
    """Creates Jira issues with formatted ADF descriptions, parent links and cross-links."""

    name: str = "Jira Issue Creator"
    description: str = "Creates Jira issues (epics and child stories) from a converted payload."
    args_schema: Type[BaseModel] = JiraIssueCreatorSchema

    base_url: str = JIRA_BASE_URL
    post_url: str = ""
    dry_run: bool = False  # when True, build payloads but do not POST

    # ----------------------------- formatting -----------------------------
    def _format_heading(self, key: str) -> str:
        key = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)
        key = key.replace('_', ' ')
        return key.capitalize()

    def _normalize_description(self, description: Any) -> str:
        """Turn a str / dict description into a markdown-ish string.

        Dict values must be str or list[str]; nested dicts are rendered as
        'key: value' lines. Anything else is stringified defensively.
        """
        if isinstance(description, str):
            return description
        if isinstance(description, dict):
            formatted = []
            for key, value in description.items():
                title = f"**{self._format_heading(key)}**"
                if isinstance(value, list):
                    items = "\n".join(f"- {self._stringify(v)}" for v in value)
                    formatted.append(f"{title}\n{items}")
                elif isinstance(value, dict):
                    nested = "\n".join(f"- {k}: {self._stringify(v)}" for k, v in value.items())
                    formatted.append(f"{title}\n{nested}")
                else:
                    formatted.append(f"{title}\n{self._stringify(value)}")
            return "\n\n".join(formatted)
        return self._stringify(description)

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    # ----------------------------- ADF builders -----------------------------
    def _parse_inline(self, text: str, id_map: Dict[str, str], base_url: str) -> List[dict]:
        content: List[dict] = []
        i = 0
        n = len(text)
        while i < n:
            # **bold**
            if text[i:i + 2] == "**":
                end = text.find("**", i + 2)
                if end != -1:
                    content.append({"type": "text", "text": text[i + 2:end],
                                    "marks": [{"type": "strong"}]})
                    i = end + 2
                    continue
            # *italic*
            if text[i] == "*":
                end = text.find("*", i + 1)
                if end != -1:
                    content.append({"type": "text", "text": text[i + 1:end],
                                    "marks": [{"type": "em"}]})
                    i = end + 1
                    continue
            # logical-id cross reference -> hyperlink if already created
            match = _TOKEN_RE.match(text, i)
            if match:
                token = match.group(0)
                if token in id_map:
                    jira_key = id_map[token]
                    content.append({"type": "text", "text": jira_key,
                                    "marks": [{"type": "link",
                                               "attrs": {"href": f"{base_url}/browse/{jira_key}"}}]})
                else:
                    content.append({"type": "text", "text": token})
                i += len(token)
                continue
            content.append({"type": "text", "text": text[i]})
            i += 1
        # ADF text nodes cannot be empty; drop any empties just in case
        return [c for c in content if c.get("text")]

    def _convert_description(self, text: str, id_map: Dict[str, str], base_url: str) -> dict:
        lines = text.split("\n")
        blocks: List[dict] = []
        bullet_buffer: List[str] = []

        def flush_bullets():
            if not bullet_buffer:
                return
            blocks.append({
                "type": "bulletList",
                "content": [
                    {"type": "listItem",
                     "content": [{"type": "paragraph",
                                  "content": self._parse_inline(item, id_map, base_url)}]}
                    for item in bullet_buffer
                ],
            })
            bullet_buffer.clear()

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                bullet_buffer.append(stripped[2:])
                continue
            flush_bullets()
            if not stripped:
                continue
            blocks.append({"type": "paragraph",
                           "content": self._parse_inline(stripped, id_map, base_url)})
        flush_bullets()

        if not blocks:  # ADF doc must have at least one block
            blocks.append({"type": "paragraph",
                           "content": [{"type": "text", "text": " "}]})
        doc = {"type": "doc", "version": 1, "content": blocks}
        return self._sanitize_adf(doc)

    # Recursively drop empty text nodes and empty containers so Jira never sees
    # "not valid ADF". Returns None for a node that should be removed.
    def _sanitize_adf(self, node: Any) -> Any:
        if not isinstance(node, dict):
            return None
        ntype = node.get("type")

        if ntype == "text":
            txt = node.get("text")
            return node if isinstance(txt, str) and txt != "" else None

        if "content" in node:
            cleaned = [c for c in (self._sanitize_adf(ch) for ch in node["content"]) if c]
            if not cleaned:
                if ntype == "doc":  # a doc must keep at least one block
                    return {"type": "doc", "version": 1,
                            "content": [{"type": "paragraph",
                                         "content": [{"type": "text", "text": " "}]}]}
                return None  # drop empty paragraph / listItem / bulletList
            node = dict(node)
            node["content"] = cleaned
            return node

        return node

    # ------------------------------- core -------------------------------
    def _resolve_parent(self, parent: Optional[str], id_map: Dict[str, str]) -> Optional[str]:
        """A parentKey may be a logical id (resolved via id_map) or a real Jira key."""
        if not parent:
            return None
        return id_map.get(parent, parent)

    def _run(self, inputJSON: Dict[str, Any]) -> str:
        results: List[str] = []
        id_map: Dict[str, str] = {}
        try:
            base_url = (inputJSON.get("baseUrl") or self.base_url or JIRA_BASE_URL).rstrip("/")
            self.base_url = base_url
            self.post_url = base_url + "/rest/api/3/issue"

            jira_user = inputJSON.get("userEmail") or JIRA_USER_EMAIL
            jira_token = inputJSON.get("apiToken") or JIRA_API_TOKEN or os.environ.get("JIRA_API_TOKEN", "")
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            auth = HTTPBasicAuth(jira_user, jira_token)

            project_key = inputJSON.get("projectKey")
            default_type = inputJSON.get("issueType") or DEFAULT_ISSUE_TYPE
            issues = inputJSON.get("issues", [])

            if not project_key:
                return "Fatal error: no projectKey provided and JIRA_PROJECT_KEY is empty."
            if not isinstance(issues, list) or not issues:
                return "Fatal error: 'issues' must be a non-empty list."

            for issue in issues:
                response = None
                summary = issue.get("summary", "<no summary>")
                try:
                    labels = issue.get("label") or issue.get("labels") or []
                    if isinstance(labels, str):
                        labels = [labels]
                    logical_id = labels[0] if labels else None

                    issue_type = issue.get("issueType") or default_type
                    issue_type = ISSUE_TYPE_MAP.get(issue_type, issue_type)

                    description_text = self._normalize_description(issue.get("description", ""))
                    description_adf = self._convert_description(description_text, id_map, base_url)

                    fields: Dict[str, Any] = {
                        "project": {"key": project_key},
                        "summary": summary,
                        "issuetype": {"name": issue_type},
                        "labels": [str(l).replace(" ", "_") for l in labels],
                        "description": description_adf,
                    }

                    parent_key = self._resolve_parent(issue.get("parentKey"), id_map)
                    if parent_key:
                        fields["parent"] = {"key": parent_key}

                    if self.dry_run:
                        # simulate a created key so links/parents can be exercised offline
                        fake_key = f"{project_key}-{len(id_map) + 1}"
                        if logical_id:
                            id_map[logical_id] = fake_key
                        results.append(f"[DRY RUN] {issue_type} '{summary}' -> {fake_key} "
                                       f"(parent={parent_key})")
                        continue

                    response = requests.post(self.post_url, json={"fields": fields},
                                             headers=headers, auth=auth)
                    if not response.ok:
                        results.append(f"Failed: {summary} -> HTTP {response.status_code} "
                                       f"| Detail: {response.text}")
                        continue

                    issue_key = response.json().get("key")
                    if logical_id and issue_key:
                        id_map[logical_id] = issue_key
                    results.append(f"{issue_type} created: {issue_key}  ({summary})")

                except requests.RequestException as e:
                    detail = response.text if response is not None else "No response received"
                    results.append(f"Failed: {summary} -> {str(e)} | Detail: {detail}")

        except Exception as e:
            return f"Fatal error: {str(e)}"

        return "\n".join(results)


# Convenience wrapper for non-agent / script use
def create_issues(payload: Dict[str, Any], dry_run: bool = False) -> str:
    tool = JiraIssueCreator()
    tool.dry_run = dry_run
    return tool._run(payload)


if __name__ == "__main__":
    # Quick self-test: build ADF for a tiny payload without hitting Jira.
    demo = {
        "projectKey": "GGMDEMOS",
        "issueType": "Epic",
        "issues": [
            {
                "summary": "EP-01: Platform Foundation & Design System",
                "issueType": "Epic",
                "label": ["EP-01", "S1"],
                "parentKey": None,
                "description": {
                    "description": "Technical foundation for the Credit Coach agent.",
                    "scope_in": ["Envoy agent registration", "Consent capture flow"],
                    "scope_out": ["Score retrieval logic (see EP-02)"],
                },
            },
            {
                "summary": "F-01.1: Envoy Agent Registration & Orchestrator Integration",
                "issueType": "Story",
                "label": ["F-01.1"],
                "parentKey": "EP-01",
                "description": {
                    "description": "Register Credit Coach as a specialist agent. Relates to EP-01.",
                    "requirements_covered": ["FR-39", "FR-26"],
                    "data_sensitivity": "Internal",
                },
            },
        ],
    }
    print(create_issues(demo, dry_run=True))
