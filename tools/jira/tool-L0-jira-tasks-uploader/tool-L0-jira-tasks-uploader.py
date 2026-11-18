import os
import re
import json
import requests
from typing import Any, Type, Dict, List, Optional, Tuple
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
    """Input schema for AWSSecretReaderPodIdentity."""
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    """Reads an AWS Secret using Pod Identity and returns its key-value dict."""

    name: str = "AWS Secret Reader with Pod Identity"
    description: str = (
        "Reads a fixed AWS Secret using Pod Identity and returns all key-value pairs."
    )
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    # Must match the secret created in AWS Secrets Manager.
    SECRET_NAME: str = "aava/temp/varun-temp-key-values"

    def _run(self) -> Dict[str, Any]:
        try:
            client = boto3.client("secretsmanager", region_name="us-east-1")
            response = client.get_secret_value(SecretId=self.SECRET_NAME)
            secret_string = response.get("SecretString", "{}")
            secret_dict = json.loads(secret_string)

            if not isinstance(secret_dict, dict):
                raise ValueError(f"Secret value is not a JSON object: {secret_dict}")

            return secret_dict

        except ClientError as exc:
            raise RuntimeError(f"Error retrieving secret: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Unexpected error: {exc}") from exc


# Preserve the original, known-working secret-loading approach.
reader = AWSSecretReaderPodIdentity()
secrets = reader._run()

JIRA_BASE_URL = secrets.get("base_url")
JIRA_USER_EMAIL = secrets.get("id")
JIRA_API_TOKEN = secrets.get("api_key")

DEFAULT_ISSUE_TYPE = "Task"
DEFAULT_LINK_TYPE = "Relates"
REQUEST_TIMEOUT_SECONDS = 30

# Map payload issue types only when the Jira project requires it.
ISSUE_TYPE_MAP: Dict[str, str] = {}

# Logical IDs used in labels and descriptions.
_TOKEN_RE = re.compile(r"(?:EP|F|FR|NFR)-\d+(?:\.\d+)*")

# Jira custom fields, for example customfield_10244.
_CUSTOMFIELD_RE = re.compile(r"^customfield_\d+$")

# Jira hierarchy parent is used only for genuine sub-task issue types.
_SUBTASK_TYPES = {"sub-task", "subtask"}


class JiraIssueCreatorSchema(BaseModel):
    """Input schema for JiraIssueCreator."""

    inputJSON: Dict[str, Any] = Field(
        ...,
        description=(
            "Jira issue creation parameters. Supports projectKey, issueType, issues, "
            "and optional linkType. Each issue may contain summary, description, "
            "issueType, label/labels, parentKey, and Jira customfield_<id> fields. "
            "For a Task, parentKey is used to create an issue link to the Feature. "
            "For a Sub-task, parentKey is sent as Jira's hierarchy parent."
        ),
    )


class JiraIssueCreator(BaseTool):
    """
    Creates Jira issues with ADF descriptions.

    Relationship handling:
    - Sub-task + parentKey: sends fields.parent.key.
    - Task/Story/other standard issue + parentKey: creates the issue without parent,
      then creates a Jira issue link to parentKey.
    """

    name: str = "Jira Issue Creator"
    description: str = (
        "Creates Jira issues. Standard issues can be linked to a Feature using "
        "parentKey; genuine Sub-tasks use parentKey as Jira's parent field."
    )
    args_schema: Type[BaseModel] = JiraIssueCreatorSchema

    base_url: str = JIRA_BASE_URL or ""
    post_url: str = ""
    dry_run: bool = False

    # ----------------------------- formatting -----------------------------
    @staticmethod
    def _format_heading(key: str) -> str:
        key = re.sub(r"([a-z])([A-Z])", r"\1 \2", key)
        key = key.replace("_", " ")
        return key.capitalize()

    @staticmethod
    def _stringify(value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False)
        return str(value)

    def _normalize_description(self, description: Any) -> str:
        """Convert a string or dictionary description to markdown-like text."""
        if isinstance(description, str):
            return description

        if isinstance(description, dict):
            formatted: List[str] = []
            for key, value in description.items():
                title = f"**{self._format_heading(str(key))}**"

                if isinstance(value, list):
                    items = "\n".join(f"- {self._stringify(item)}" for item in value)
                    formatted.append(f"{title}\n{items}")
                elif isinstance(value, dict):
                    nested = "\n".join(
                        f"- {nested_key}: {self._stringify(nested_value)}"
                        for nested_key, nested_value in value.items()
                    )
                    formatted.append(f"{title}\n{nested}")
                else:
                    formatted.append(f"{title}\n{self._stringify(value)}")

            return "\n\n".join(formatted)

        return self._stringify(description)

    # ----------------------------- ADF builders -----------------------------
    def _parse_inline(
        self,
        text: str,
        id_map: Dict[str, str],
        base_url: str,
    ) -> List[dict]:
        content: List[dict] = []
        index = 0

        while index < len(text):
            # **bold**
            if text[index:index + 2] == "**":
                end = text.find("**", index + 2)
                if end != -1:
                    content.append(
                        {
                            "type": "text",
                            "text": text[index + 2:end],
                            "marks": [{"type": "strong"}],
                        }
                    )
                    index = end + 2
                    continue

            # *italic*
            if text[index] == "*":
                end = text.find("*", index + 1)
                if end != -1:
                    content.append(
                        {
                            "type": "text",
                            "text": text[index + 1:end],
                            "marks": [{"type": "em"}],
                        }
                    )
                    index = end + 1
                    continue

            # Logical ID cross-reference.
            match = _TOKEN_RE.match(text, index)
            if match:
                token = match.group(0)
                if token in id_map:
                    jira_key = id_map[token]
                    content.append(
                        {
                            "type": "text",
                            "text": jira_key,
                            "marks": [
                                {
                                    "type": "link",
                                    "attrs": {
                                        "href": f"{base_url}/browse/{jira_key}"
                                    },
                                }
                            ],
                        }
                    )
                else:
                    content.append({"type": "text", "text": token})

                index += len(token)
                continue

            content.append({"type": "text", "text": text[index]})
            index += 1

        return [node for node in content if node.get("text")]

    def _convert_description(
        self,
        text: str,
        id_map: Dict[str, str],
        base_url: str,
    ) -> dict:
        blocks: List[dict] = []
        bullet_buffer: List[str] = []

        def flush_bullets() -> None:
            if not bullet_buffer:
                return

            blocks.append(
                {
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": self._parse_inline(
                                        item, id_map, base_url
                                    ),
                                }
                            ],
                        }
                        for item in bullet_buffer
                    ],
                }
            )
            bullet_buffer.clear()

        for line in text.split("\n"):
            stripped = line.strip()

            if stripped.startswith("- "):
                bullet_buffer.append(stripped[2:])
                continue

            flush_bullets()

            if stripped:
                blocks.append(
                    {
                        "type": "paragraph",
                        "content": self._parse_inline(stripped, id_map, base_url),
                    }
                )

        flush_bullets()

        if not blocks:
            blocks.append(
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": " "}],
                }
            )

        document = {"type": "doc", "version": 1, "content": blocks}
        return self._sanitize_adf(document)

    def _sanitize_adf(self, node: Any) -> Any:
        """Remove empty ADF text nodes and empty containers recursively."""
        if not isinstance(node, dict):
            return None

        node_type = node.get("type")

        if node_type == "text":
            text = node.get("text")
            return node if isinstance(text, str) and text != "" else None

        if "content" in node:
            cleaned = [
                child
                for child in (
                    self._sanitize_adf(child) for child in node["content"]
                )
                if child
            ]

            if not cleaned:
                if node_type == "doc":
                    return {
                        "type": "doc",
                        "version": 1,
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [{"type": "text", "text": " "}],
                            }
                        ],
                    }
                return None

            sanitized = dict(node)
            sanitized["content"] = cleaned
            return sanitized

        return node

    # ------------------------------- helpers -------------------------------
    @staticmethod
    def _resolve_parent(
        parent: Optional[str],
        id_map: Dict[str, str],
    ) -> Optional[str]:
        """Resolve a logical parent ID or return an existing Jira key."""
        if not parent:
            return None
        return id_map.get(parent, parent)

    @staticmethod
    def _extract_custom_fields(issue: Dict[str, Any]) -> Dict[str, Any]:
        """Pass Jira customfield_<id> values through unchanged."""
        return {
            key: value
            for key, value in issue.items()
            if isinstance(key, str)
            and _CUSTOMFIELD_RE.match(key)
            and value is not None
        }

    @staticmethod
    def _is_subtask(issue_type: str) -> bool:
        return issue_type.strip().lower() in _SUBTASK_TYPES

    def _create_issue_link(
        self,
        feature_key: str,
        created_issue_key: str,
        link_type: str,
        headers: Dict[str, str],
        auth: HTTPBasicAuth,
    ) -> Tuple[bool, str]:
        """
        Link a newly-created standard issue to a Feature.

        The link call is tried twice. The issue creation call is never repeated here,
        which prevents duplicate Tasks when creation succeeds but linking fails.
        """
        link_url = f"{self.base_url}/rest/api/3/issueLink"
        link_payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": feature_key},
            "outwardIssue": {"key": created_issue_key},
        }

        last_error = "Unknown issue-link error"

        for _ in range(2):
            try:
                response = requests.post(
                    link_url,
                    json=link_payload,
                    headers=headers,
                    auth=auth,
                    timeout=REQUEST_TIMEOUT_SECONDS,
                )

                if response.ok:
                    return True, ""

                last_error = (
                    f"HTTP {response.status_code} | Detail: {response.text}"
                )

            except requests.RequestException as exc:
                last_error = str(exc)

        return False, last_error

    # -------------------------------- core --------------------------------
    def _run(self, inputJSON: Dict[str, Any]) -> str:
        results: List[str] = []
        id_map: Dict[str, str] = {}

        try:
            base_url_value = inputJSON.get("baseUrl") or self.base_url or JIRA_BASE_URL
            if not base_url_value:
                return "Fatal error: Jira base URL is missing from AWS Secrets Manager."

            base_url = str(base_url_value).rstrip("/")
            self.base_url = base_url
            self.post_url = f"{base_url}/rest/api/3/issue"

            jira_user = inputJSON.get("userEmail") or JIRA_USER_EMAIL
            jira_token = (
                inputJSON.get("apiToken")
                or JIRA_API_TOKEN
                or os.environ.get("JIRA_API_TOKEN", "")
            )

            if not jira_user:
                return "Fatal error: Jira user email is missing."
            if not jira_token:
                return "Fatal error: Jira API token is missing."

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            auth = HTTPBasicAuth(str(jira_user), str(jira_token))

            project_key = inputJSON.get("projectKey")
            default_type = inputJSON.get("issueType") or DEFAULT_ISSUE_TYPE
            link_type = inputJSON.get("linkType") or DEFAULT_LINK_TYPE
            issues = inputJSON.get("issues", [])

            if not project_key:
                return "Fatal error: no projectKey provided."

            if not isinstance(issues, list) or not issues:
                return "Fatal error: 'issues' must be a non-empty list."

            for issue in issues:
                response: Optional[requests.Response] = None
                summary = issue.get("summary", "<no summary>")

                try:
                    labels = issue.get("label") or issue.get("labels") or []
                    if isinstance(labels, str):
                        labels = [labels]

                    logical_id = labels[0] if labels else None

                    issue_type = issue.get("issueType") or default_type
                    issue_type = ISSUE_TYPE_MAP.get(issue_type, issue_type)

                    parent_key = self._resolve_parent(
                        issue.get("parentKey"), id_map
                    )

                    description_text = self._normalize_description(
                        issue.get("description", "")
                    )
                    description_adf = self._convert_description(
                        description_text,
                        id_map,
                        base_url,
                    )

                    fields: Dict[str, Any] = {
                        "project": {"key": project_key},
                        "summary": summary,
                        "issuetype": {"name": issue_type},
                        "labels": [
                            str(label).replace(" ", "_") for label in labels
                        ],
                        "description": description_adf,
                    }

                    fields.update(self._extract_custom_fields(issue))

                    # Use Jira's parent field only for a genuine Sub-task.
                    # A Task cannot use a Feature as its hierarchy parent when the Jira
                    # hierarchy does not allow it. Standard issues are linked afterward.
                    if parent_key and self._is_subtask(issue_type):
                        fields["parent"] = {"key": parent_key}

                    if self.dry_run:
                        fake_key = f"{project_key}-{len(id_map) + 1}"

                        if logical_id:
                            id_map[logical_id] = fake_key

                        if parent_key and self._is_subtask(issue_type):
                            relationship = f"parent={parent_key}"
                        elif parent_key:
                            relationship = (
                                f"linked_feature={parent_key}, link_type={link_type}"
                            )
                        else:
                            relationship = "no_relationship"

                        results.append(
                            f"[DRY RUN] {issue_type} '{summary}' -> {fake_key} "
                            f"({relationship})"
                        )
                        continue

                    response = requests.post(
                        self.post_url,
                        json={"fields": fields},
                        headers=headers,
                        auth=auth,
                        timeout=REQUEST_TIMEOUT_SECONDS,
                    )

                    if not response.ok:
                        results.append(
                            f"Failed: {summary} -> HTTP {response.status_code} "
                            f"| Detail: {response.text}"
                        )
                        continue

                    try:
                        response_body = response.json()
                    except ValueError:
                        results.append(
                            f"Failed: {summary} -> Jira returned non-JSON success "
                            f"response | Detail: {response.text}"
                        )
                        continue

                    issue_key = response_body.get("key")
                    if not issue_key:
                        results.append(
                            f"Failed: {summary} -> Jira returned success without "
                            f"an issue key | Detail: {response.text}"
                        )
                        continue

                    if logical_id:
                        id_map[logical_id] = issue_key

                    # Keep this exact prefix for evaluator key extraction.
                    results.append(
                        f"{issue_type} created: {issue_key}  ({summary})"
                    )
                    results.append(f"url: {base_url}/browse/{issue_key}")

                    # Standard issues are linked to the supplied Feature after creation.
                    if parent_key and not self._is_subtask(issue_type):
                        linked, link_error = self._create_issue_link(
                            feature_key=parent_key,
                            created_issue_key=issue_key,
                            link_type=str(link_type),
                            headers=headers,
                            auth=auth,
                        )

                        if linked:
                            results.append(
                                f"Linked: {issue_key} -> {parent_key} "
                                f"(type={link_type})"
                            )
                        else:
                            # The Task was created successfully. Do not recreate it.
                            results.append(
                                f"Link failed: {issue_key} -> {parent_key} "
                                f"(type={link_type}) | Detail: {link_error}"
                            )

                except requests.RequestException as exc:
                    detail = (
                        response.text
                        if response is not None
                        else "No response received"
                    )
                    results.append(
                        f"Failed: {summary} -> {exc} | Detail: {detail}"
                    )

                except Exception as exc:
                    results.append(f"Failed: {summary} -> {exc}")

        except Exception as exc:
            return f"Fatal error: {exc}"

        return "\n".join(results)


# Convenience wrapper for non-agent/script use.
def create_issues(payload: Dict[str, Any], dry_run: bool = False) -> str:
    tool = JiraIssueCreator()
    tool.dry_run = dry_run
    return tool._run(payload)
