import json
import re
from typing import Any, Dict, List, Optional, Tuple, Type

import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


# Jira issue keys are treated as identifiers, never as arbitrary JQL fragments.
# ASCII + fullmatch prevents quotes, whitespace, operators, comments and control
# characters from entering a JQL literal.
JIRA_KEY_PATTERN = re.compile(r"[A-Z][A-Z0-9_]*-[0-9]+", re.ASCII)


def _validate_jira_key(value: Any, *, field_name: str = "Jira issue key") -> str:
    """Return a canonical Jira key or reject untrusted input."""
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    key = value.strip().upper()
    if not key or len(key) > 255 or JIRA_KEY_PATTERN.fullmatch(key) is None:
        raise ValueError(
            f"Invalid {field_name}. Expected a key such as E2ESFI-14; "
            "quotes, whitespace within the key, JQL operators and special "
            "characters are not allowed."
        )
    return key


def _jql_key_literal(value: Any) -> str:
    """Build a quoted JQL string literal only from a validated Jira key."""
    key = _validate_jira_key(value)
    # The grammar above excludes both quote and backslash. Keep explicit
    # escaping here as defense in depth if the accepted grammar ever changes.
    escaped = key.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


class XrayJiraReaderSchema(BaseModel):
    """Input schema: inputJSON accepts all documented Jira-reader input shapes."""

    inputJSON: Any = Field(
        ...,
        description=(
            "A dict such as {'key':'E2ESFI-14'} or "
            "{'keys':['E2ESFI-14','E2ESFI-35']}; also accepts a list, JSON string, "
            "comma-separated Jira keys, or a single Jira key. Optional maxDepth "
            "and includeChildren control recursive child retrieval."
        ),
    )


class JiraIssueFetchError(RuntimeError):
    def __init__(self, status_code: Any, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class XrayJiraReaderTool(BaseTool):
    name: str = "tool-L0-xray-reader"
    description: str = (
        "Reads one or more Jira issues and recursively walks their child work "
        "items, retrieving Xray Tests for each supported issue. Accepts inputJSON "
        "as a dict, list, JSON string, comma-separated string, or single key. "
        "Read-only; Jira and Xray credentials are loaded from AVASecret."
    )
    args_schema: Type[BaseModel] = XrayJiraReaderSchema

    # Deployment configuration.
    DEFAULT_XRAY_BASE_URL: str = "https://eu.xray.cloud.getxray.app"
    DEFAULT_MAX_DEPTH: int = 5
    PAGE_SIZE: int = 100
    REQUEST_TIMEOUT_SECONDS: int = 30

    # ------------------------------------------------------------------
    # Input normalization: intentionally mirrors tool-L0-jira-reader.
    # ------------------------------------------------------------------
    def _normalize_input(self, raw: Any) -> Tuple[List[str], bool, int, bool]:
        """Return (normalized_keys, output_is_array, max_depth, include_children)."""
        payload: Any = raw
        output_is_array = False

        if isinstance(payload, str):
            candidate = payload.strip()
            if not candidate:
                raise ValueError("Provide 'key' or 'keys' in inputJSON.")

            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, (dict, list)):
                    payload = parsed
                elif isinstance(parsed, str):
                    payload = parsed
                else:
                    payload = candidate
            except json.JSONDecodeError:
                payload = candidate

            if isinstance(payload, str):
                if "," in payload:
                    payload = [
                        part.strip() for part in payload.split(",")
                        if part.strip()
                    ]
                    output_is_array = True
                else:
                    payload = {"key": payload}

        if isinstance(payload, list):
            keys_value = payload
            options: Dict[str, Any] = {}
            output_is_array = True
        elif isinstance(payload, dict):
            options = payload
            if "keys" in payload and payload.get("keys") is not None:
                keys_value = payload.get("keys")
                output_is_array = True
            elif "key" in payload:
                keys_value = [payload.get("key")]
                output_is_array = False
            else:
                raise ValueError(
                    "Fatal error: provide 'key' (string) or 'keys' (list)."
                )
        else:
            raise ValueError(
                "inputJSON must be a dict, list, JSON string, CSV string, or Jira key."
            )

        if isinstance(keys_value, str):
            # A string in `keys` is one key, not a comma-separated list.
            keys = [keys_value]
        elif isinstance(keys_value, list):
            keys = keys_value
        elif isinstance(keys_value, dict):
            # Accept a single structured issue object as well as a string key.
            keys = [keys_value]
        else:
            raise ValueError(
                "'key' must be a Jira key string; 'keys' must be a string, "
                "a list of strings, or a list of Jira issue objects."
            )

        def extract_issue_key(item: Any, index: int) -> str:
            if isinstance(item, str):
                return item

            # Agent/workflow outputs sometimes pass issue records instead of
            # a flat list of strings. Extract only recognized Jira-key fields.
            if isinstance(item, dict):
                candidate_fields = (
                    "key",
                    "jira_issue_id",
                    "jira_key",
                    "issue_key",
                    "issue_id",
                )
                for field_name in candidate_fields:
                    value = item.get(field_name)
                    if isinstance(value, str) and value.strip():
                        return value

                # Support the common nested Jira issue envelope.
                nested = item.get("jira_issue")
                if isinstance(nested, dict):
                    value = nested.get("key")
                    if isinstance(value, str) and value.strip():
                        return value

                raise ValueError(
                    f"Invalid issue item at index {index}: expected a Jira key "
                    f"string or an object containing one of {', '.join(candidate_fields)}."
                )

            # Support Pydantic-style objects passed directly by an agent runtime.
            for field_name in ("key", "jira_issue_id", "jira_key", "issue_key", "issue_id"):
                value = getattr(item, field_name, None)
                if isinstance(value, str) and value.strip():
                    return value

            raise ValueError(
                f"Invalid issue item at index {index}: expected a Jira key string "
                f"or Jira issue object; received {type(item).__name__}."
            )

        normalized_keys: List[str] = []
        for index, item in enumerate(keys):
            raw_key = extract_issue_key(item, index)
            key = raw_key.strip().upper()
            if not JIRA_KEY_PATTERN.fullmatch(key):
                raise ValueError(
                    f"Invalid Jira issue key '{raw_key}' at index {index}. "
                    "Expected format such as E2ESFI-14."
                )
            normalized_keys.append(key)

        if not normalized_keys:
            raise ValueError("Provide at least one Jira issue key.")

        max_depth_raw = options.get("maxDepth", self.DEFAULT_MAX_DEPTH)
        # Jira-reader README semantics: 0, null, and omitted all mean default 5.
        if max_depth_raw in (None, 0):
            max_depth = self.DEFAULT_MAX_DEPTH
        else:
            if isinstance(max_depth_raw, bool):
                raise ValueError("'maxDepth' must be a non-negative integer.")
            try:
                max_depth = int(max_depth_raw)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    "'maxDepth' must be a non-negative integer."
                ) from exc
            if max_depth < 0:
                raise ValueError("'maxDepth' must be a non-negative integer.")

        # Deliberately mirrors the Jira-reader README: bool("false") is True.
        include_children = bool(options.get("includeChildren", True))
        return normalized_keys, output_is_array, max_depth, include_children

    # ------------------------------------------------------------------
    # Credentials and HTTP helpers.
    # ------------------------------------------------------------------
    def _load_credentials(self) -> Dict[str, str]:
        """Load Jira and Xray credentials at runtime, not module import."""
        import AVASecret

        try:
            credentials = {
                "jira_api_token": AVASecret.getValue("api_key"),
                "jira_user": AVASecret.getValue("id"),
                "jira_base_url": AVASecret.getValue("base_url") or AVASecret.getValue("jira_base_url"),
                "xray_client_id": AVASecret.getValue("xray_client_id"),
                "xray_client_secret": AVASecret.getValue("xray_client_secret"),
                "xray_base_url": (
                    AVASecret.getValue("xray_base_url") or self.DEFAULT_XRAY_BASE_URL
                ),
            }
        except Exception as exc:
            raise RuntimeError(
                f"Unable to read secrets from AVASecret: {exc}"
            ) from exc

        try:
            missing = [key for key, value in credentials.items() if not value]
            if missing:
                raise ValueError(
                    "AVASecret is missing required keys: " + ", ".join(missing)
                )

            credentials["jira_base_url"] = (
                credentials["jira_base_url"].strip().rstrip("/")
            )
            if not credentials["jira_base_url"].startswith(("http://", "https://")):
                credentials["jira_base_url"] = "https://" + credentials["jira_base_url"]

            credentials["xray_base_url"] = (
                credentials["xray_base_url"].strip().rstrip("/")
            )
            if not credentials["xray_base_url"].startswith(("http://", "https://")):
                raise ValueError("xray_base_url must start with http:// or https://.")

            return credentials

        except Exception as exc:
            raise RuntimeError(f"Credential loading failed: {exc}") from exc

    def _get_xray_token(self, credentials: Dict[str, str]) -> str:
        url = f"{credentials['xray_base_url']}/api/v2/authenticate"
        response = requests.post(
            url,
            json={
                "client_id": credentials["xray_client_id"],
                "client_secret": credentials["xray_client_secret"],
            },
            timeout=(5, self.REQUEST_TIMEOUT_SECONDS),
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Xray authentication failed (HTTP {response.status_code}): "
                f"{response.text[:1500]}"
            )

        token = response.text.strip().strip('"')
        if not token:
            raise RuntimeError("Xray authentication returned an empty token.")
        return token

    @staticmethod
    def _response_detail(response: requests.Response) -> str:
        try:
            body = response.text
        except Exception:
            body = ""
        return body[:2000] or "No response detail supplied."

    def _fetch_issue(
        self, jira_issue_id: str, credentials: Dict[str, str]
    ) -> Dict[str, Any]:
        jira_issue_id = _validate_jira_key(jira_issue_id)
        url = (
            f"{credentials['jira_base_url']}/rest/api/3/issue/"
            f"{jira_issue_id}"
        )
        response = requests.get(
            url,
            auth=(credentials["jira_user"], credentials["jira_api_token"]),
            headers={"Accept": "application/json"},
            params={"fields": "*all"},
            timeout=(5, self.REQUEST_TIMEOUT_SECONDS),
        )

        if response.status_code != 200:
            raise JiraIssueFetchError(
                response.status_code,
                self._response_detail(response),
            )

        try:
            issue = response.json()
        except ValueError as exc:
            raise JiraIssueFetchError(
                response.status_code, "Jira returned a non-JSON issue response."
            ) from exc

        if not isinstance(issue, dict) or not isinstance(issue.get("fields"), dict):
            raise JiraIssueFetchError(
                response.status_code, "Jira issue response did not contain fields."
            )
        return issue

    def _fetch_children(
        self, parent_key: str, credentials: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """Fetch direct children using Jira parent JQL; failures become leaf nodes."""
        parent_literal = _jql_key_literal(parent_key)
        endpoint = f"{credentials['jira_base_url']}/rest/api/3/search/jql"
        children: List[Dict[str, Any]] = []
        next_page_token: Optional[str] = None

        while True:
            payload: Dict[str, Any] = {
                "jql": f"parent = {parent_literal} ORDER BY created ASC",
                "maxResults": self.PAGE_SIZE,
                "fields": ["*all"],
            }
            if next_page_token:
                payload["nextPageToken"] = next_page_token

            try:
                response = requests.post(
                    endpoint,
                    auth=(credentials["jira_user"], credentials["jira_api_token"]),
                    headers={
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=(5, self.REQUEST_TIMEOUT_SECONDS),
                )
                if response.status_code != 200:
                    return []
                body = response.json()
                if not isinstance(body, dict):
                    return []
            except (requests.RequestException, ValueError):
                return []

            page_issues = body.get("issues") or []
            if not isinstance(page_issues, list):
                return []

            children.extend(
                issue for issue in page_issues
                if isinstance(issue, dict) and issue.get("key")
            )
            next_page_token = body.get("nextPageToken")
            if not next_page_token:
                break

        return children

    # ------------------------------------------------------------------
    # Jira field normalization (same output fields as Jira reader).
    # ------------------------------------------------------------------
    @staticmethod
    def _display_name(value: Any) -> Optional[str]:
        if isinstance(value, dict):
            return value.get("displayName") or value.get("name") or value.get("emailAddress")
        return None

    @staticmethod
    def _adf_to_text(value: Any) -> Optional[str]:
        """Flatten Jira ADF descriptions to readable plain text."""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        if not isinstance(value, dict):
            return str(value)

        def render(node: Any) -> str:
            if isinstance(node, list):
                return "".join(render(item) for item in node)
            if not isinstance(node, dict):
                return ""

            node_type = node.get("type")
            if node_type == "text":
                return str(node.get("text", ""))
            if node_type == "hardBreak":
                return "\n"

            content = node.get("content") or []
            if node_type == "bulletList":
                rows = []
                for item in content:
                    text = render(item).strip()
                    if text:
                        rows.append("- " + text)
                return "\n".join(rows) + ("\n" if rows else "")
            if node_type == "orderedList":
                rows = []
                start = int((node.get("attrs") or {}).get("order", 1))
                for index, item in enumerate(content, start=start):
                    text = render(item).strip()
                    if text:
                        rows.append(f"{index}. {text}")
                return "\n".join(rows) + ("\n" if rows else "")
            rendered = render(content)

            if node_type in ("paragraph", "heading", "blockquote", "codeBlock"):
                return rendered.rstrip() + "\n"
            if node_type == "listItem":
                return rendered.strip()
            if node_type == "doc":
                return rendered
            return rendered

        result = render(value).strip()
        return result

    def _issue_node(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        fields = issue.get("fields") or {}
        issue_type = (fields.get("issuetype") or {}).get("name")
        labels = fields.get("labels") or []
        if not isinstance(labels, list):
            labels = []

        return {
            "issue_id": issue.get("key"),
            "title": fields.get("summary"),
            "status": (fields.get("status") or {}).get("name"),
            "description": self._adf_to_text(fields.get("description")),
            "labels": labels,
            "assignee": self._display_name(fields.get("assignee")),
            "due_date": fields.get("duedate"),
            "reporter": self._display_name(fields.get("reporter")),
            "issue_type": issue_type,
            "child_work_item_ids": [],
            "xray_retrieval": {},
            "children": [],
        }

    # ------------------------------------------------------------------
    # Xray retrieval. Xray auth token is acquired once per invocation.
    # ------------------------------------------------------------------
    def _query_xray_tests(
        self,
        jira_issue_id: str,
        issue_type: str,
        credentials: Dict[str, str],
        token: str,
    ) -> List[Dict[str, Any]]:
        jira_issue_id = _validate_jira_key(
            jira_issue_id, field_name="Xray Jira issue key"
        )
        key_literal = _jql_key_literal(jira_issue_id)

        normalized_type = (issue_type or "").strip().lower()
        if normalized_type == "test":
            jql = f"key = {key_literal}"
        elif normalized_type in ("story", "requirement"):
            jql = f"issue in requirementTests({key_literal})"
        else:
            raise NotImplementedError(
                f"Jira issue type '{issue_type or 'Unknown'}' is not a supported "
                "Xray retrieval root. Supported types: Test, Story, Requirement."
            )

        gql_url = f"{credentials['xray_base_url']}/api/v2/graphql"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        query = """
        query GetTests($jql: String!, $limit: Int!, $start: Int!) {
          getTests(jql: $jql, limit: $limit, start: $start) {
            total
            start
            limit
            results {
              issueId
              testType {
                name
                kind
              }
              jira(fields: [
                "key",
                "summary",
                "description",
                "issuetype",
                "status",
                "priority",
                "labels"
              ])
              steps {
                id
                action
                data
                result
              }
            }
          }
        }
        """

        all_tests: List[Dict[str, Any]] = []
        start = 0
        total: Optional[int] = None

        while total is None or start < total:
            payload = {
                "query": query,
                "variables": {
                    "jql": jql,
                    "limit": self.PAGE_SIZE,
                    "start": start,
                },
            }
            response = requests.post(
                gql_url,
                headers=headers,
                json=payload,
                timeout=(5, self.REQUEST_TIMEOUT_SECONDS),
            )

            if response.status_code in (401, 403):
                raise PermissionError(
                    f"Xray GraphQL permission failure (HTTP {response.status_code}): "
                    f"{self._response_detail(response)}"
                )
            if response.status_code != 200:
                raise RuntimeError(
                    f"Xray GraphQL request failed (HTTP {response.status_code}): "
                    f"{self._response_detail(response)}"
                )

            try:
                body = response.json()
            except ValueError as exc:
                raise RuntimeError(
                    f"Xray returned non-JSON response: {self._response_detail(response)}"
                ) from exc

            if not isinstance(body, dict):
                raise RuntimeError("Xray GraphQL response was not a JSON object.")
            if body.get("errors"):
                raise RuntimeError(
                    "Xray GraphQL returned errors: "
                    + json.dumps(body["errors"], ensure_ascii=False)
                )

            result = (body.get("data") or {}).get("getTests")
            if not isinstance(result, dict):
                raise RuntimeError(
                    "Unexpected Xray GraphQL response: "
                    + json.dumps(body, ensure_ascii=False)[:2000]
                )

            page_results = result.get("results") or []
            if not isinstance(page_results, list):
                raise RuntimeError("Xray GraphQL 'results' was not a list.")

            all_tests.extend(page_results)
            total = int(result.get("total") or 0)

            if not page_results:
                break
            start += len(page_results)

        return all_tests

    def _attach_xray_result(
        self,
        node: Dict[str, Any],
        credentials: Dict[str, str],
        token: str,
    ) -> None:
        issue_key = node["issue_id"]
        issue_type = node.get("issue_type") or ""

        try:
            tests = self._query_xray_tests(
                issue_key, issue_type, credentials, token
            )
            retrieval_method = (
                "exact_test_lookup"
                if issue_type.strip().lower() == "test"
                else "requirement_coverage_lookup"
            )
            node["xray_retrieval"] = {
                "retrieval_status": "SUCCESS" if tests else "NO_TESTS_FOUND",
                "retrieval_method": retrieval_method,
                "total_test_cases": len(tests),
                "test_cases": tests,
            }
        except NotImplementedError as exc:
            node["xray_retrieval"] = {
                "retrieval_status": "UNSUPPORTED_ISSUE_TYPE",
                "retrieval_method": "not_completed",
                "total_test_cases": 0,
                "test_cases": [],
                "message": str(exc),
            }
        except PermissionError as exc:
            node["xray_retrieval"] = {
                "retrieval_status": "PERMISSION_ERROR",
                "retrieval_method": "not_completed",
                "total_test_cases": 0,
                "test_cases": [],
                "message": str(exc),
            }
        except Exception as exc:
            node["xray_retrieval"] = {
                "retrieval_status": "FAILED",
                "retrieval_method": "not_completed",
                "total_test_cases": 0,
                "test_cases": [],
                "message": str(exc),
            }

    # ------------------------------------------------------------------
    # Recursive tree builder.
    # ------------------------------------------------------------------
    def _build_tree(
        self,
        issue: Dict[str, Any],
        credentials: Dict[str, str],
        token: str,
        depth: int,
        max_depth: int,
        include_children: bool,
        visited: set,
    ) -> Dict[str, Any]:
        node = self._issue_node(issue)
        key = node["issue_id"]
        self._attach_xray_result(node, credentials, token)

        if not include_children or depth >= max_depth or key in visited:
            return node

        visited.add(key)
        child_issues = self._fetch_children(key, credentials)
        node["child_work_item_ids"] = [
            child.get("key") for child in child_issues if child.get("key")
        ]

        for child_issue in child_issues:
            child_key = child_issue.get("key")
            if not child_key or child_key in visited:
                continue
            node["children"].append(
                self._build_tree(
                    child_issue,
                    credentials,
                    token,
                    depth + 1,
                    max_depth,
                    include_children,
                    visited,
                )
            )
        return node

    # ------------------------------------------------------------------
    # Tool entrypoint.
    # ------------------------------------------------------------------
    def _run(self, inputJSON: Any) -> str:
        try:
            keys, output_is_array, max_depth, include_children = (
                self._normalize_input(inputJSON)
            )
            credentials = self._load_credentials()
            # One Xray authentication per tool invocation; reuse token for all nodes.
            token = self._get_xray_token(credentials)

            results: List[Dict[str, Any]] = []
            for key in keys:
                try:
                    root_issue = self._fetch_issue(key, credentials)
                    tree = self._build_tree(
                        root_issue,
                        credentials,
                        token,
                        depth=0,
                        max_depth=max_depth,
                        include_children=include_children,
                        visited=set(),
                    )
                    results.append(tree)
                except JiraIssueFetchError as exc:
                    results.append({
                        "issue_id": key,
                        "error": f"HTTP {exc.status_code}",
                        "detail": exc.detail,
                    })
                except Exception as exc:
                    results.append({
                        "issue_id": key,
                        "error": "RETRIEVAL_ERROR",
                        "detail": str(exc),
                    })

            # Jira-reader output shape: `key` -> object; `keys`/list/CSV -> array.
            output: Any = results if output_is_array else results[0]
            return json.dumps(output, ensure_ascii=False)

        except Exception as exc:
            return f"Fatal error: {exc}"


# Backward-compatible import aliases.
XrayReader = XrayJiraReaderTool
XrayJiraReader = XrayJiraReaderTool
