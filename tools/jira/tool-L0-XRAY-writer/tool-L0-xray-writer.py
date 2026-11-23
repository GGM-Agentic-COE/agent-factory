import json
import time
from typing import Any, Dict, List, Optional, Type

import boto3
import requests
import urllib3
from botocore.exceptions import ClientError
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AWSSecretReaderPodIdentitySchema(BaseModel):
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = (
        "Reads a fixed AWS Secret using Pod Identity and returns all key value pairs as a dict"
    )
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    # SETUP-REQUIRED
    SECRET_NAME: str = "aava/temp/varun-temp-key-values"
    AWS_REGION: str = "us-east-1"

    def _run(self) -> Dict[str, Any]:
        try:
            client = boto3.client("secretsmanager", region_name=self.AWS_REGION)
            response = client.get_secret_value(SecretId=self.SECRET_NAME)
            secret_dict = json.loads(response.get("SecretString", "{}"))
            if not isinstance(secret_dict, dict):
                raise ValueError("Secret value is not a JSON object")
            return secret_dict
        except ClientError as exc:
            raise RuntimeError(f"Error retrieving secret: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Unexpected error: {exc}") from exc


reader = AWSSecretReaderPodIdentity()
secrets = reader._run()

api_key = secrets.get("api_key")
user_email = secrets.get("id")
jira_base_url = secrets.get("base_url") or secrets.get("jira_base_url")
xray_client_id = secrets.get("xray_client_id")
xray_client_secret = secrets.get("xray_client_secret")
xray_base_url = (
    secrets.get("xray_base_url") or "https://eu.xray.cloud.getxray.app"
).strip().rstrip("/")

_missing = [
    key
    for key, value in (
        ("api_key", api_key),
        ("user_email", user_email),
        ("jira_base_url", jira_base_url),
        ("xray_client_id", xray_client_id),
        ("xray_client_secret", xray_client_secret),
    )
    if not value
]
if _missing:
    raise RuntimeError(
        f"Secret '{AWSSecretReaderPodIdentity.SECRET_NAME}' is missing keys: {_missing}"
    )

jira_base_url = str(jira_base_url).strip().rstrip("/")
if not jira_base_url.startswith(("http://", "https://")):
    jira_base_url = f"https://{jira_base_url}"

jira_auth = (user_email, api_key)


class XrayJiraCompleteTraceabilitySchema(BaseModel):
    project_key: str = Field(default="", description="Target Jira project key")
    story_key: str = Field(default="", description="Jira Feature or Story key to link Tests to")
    tests_json: Any = Field(
        default="[]",
        description=(
            "JSON string dict or list of tests Each test must contain test_representation "
            "manual or cucumber Manual tests require steps Cucumber tests require gherkin"
        ),
    )


class _XrayTestFormatter:
    @staticmethod
    def normalize_tests(tests_data: Any) -> List[Dict[str, Any]]:
        data = tests_data
        for _ in range(2):
            if isinstance(data, str):
                try:
                    data = json.loads(data.strip())
                except Exception:
                    break

        if isinstance(data, dict):
            for key in ("tests", "test_cases", "data"):
                if key in data and isinstance(data[key], (list, dict)):
                    data = data[key]
                    break

        if isinstance(data, dict):
            return [data]
        if not isinstance(data, list):
            return []

        normalized: List[Dict[str, Any]] = []
        for item in data:
            if isinstance(item, dict):
                normalized.append(item)
            elif isinstance(item, str):
                try:
                    parsed = json.loads(item)
                    if isinstance(parsed, dict):
                        normalized.append(parsed)
                except Exception:
                    continue
        return normalized

    @staticmethod
    def get_representation(test: Dict[str, Any]) -> str:
        value = test.get("test_representation") or test.get("test_type") or ""
        normalized = str(value).strip().lower()
        aliases = {
            "manual": "manual",
            "cucumber": "cucumber",
            "gherkin": "cucumber",
            "review": "review",
        }
        return aliases.get(normalized, normalized)

    @staticmethod
    def format_steps(raw_steps: Any) -> List[Dict[str, str]]:
        if isinstance(raw_steps, str):
            try:
                raw_steps = json.loads(raw_steps)
            except Exception as exc:
                raise ValueError("Manual test steps must be a JSON list or object") from exc
        if isinstance(raw_steps, dict):
            raw_steps = [raw_steps]
        if not isinstance(raw_steps, list):
            raise ValueError("Manual test requires a steps list")

        formatted: List[Dict[str, str]] = []
        for index, step in enumerate(raw_steps, start=1):
            if not isinstance(step, dict):
                raise ValueError(f"Manual step {index} must be an object")
            action = str(step.get("action") or "").strip()
            data = str(step.get("data") or step.get("test_data") or "").strip()
            result = str(step.get("expected_result") or step.get("result") or "").strip()
            if not action:
                raise ValueError(f"Manual step {index} is missing action")
            if not result:
                raise ValueError(f"Manual step {index} is missing expected_result")
            formatted.append({"action": action, "data": data, "result": result})

        if not formatted:
            raise ValueError("Manual test requires at least one step")
        return formatted

    @staticmethod
    def extract_gherkin(test: Dict[str, Any]) -> str:
        gherkin = test.get("gherkin") or test.get("gherkin_definition") or test.get("scenario")
        if not isinstance(gherkin, str) or not gherkin.strip():
            raise ValueError("Cucumber test requires non-empty gherkin content")
        text = gherkin.strip()
        if not (text.startswith("Scenario:") or text.startswith("Scenario Outline:")):
            raise ValueError("Cucumber gherkin must start with Scenario or Scenario Outline")
        required = ("\n  Given ", "\n  When ", "\n  Then ")
        missing = [keyword.strip() for keyword in required if keyword not in text]
        if missing:
            raise ValueError(f"Cucumber gherkin is missing required keywords: {missing}")
        return text

    @staticmethod
    def extract_precondition(test: Dict[str, Any]) -> Optional[Dict[str, str]]:
        raw = test.get("pre_condition") or test.get("precondition") or test.get("preconditions")
        if not raw:
            return None
        if isinstance(raw, dict):
            summary = raw.get("summary") or raw.get("title")
            definition = raw.get("definition") or raw.get("description")
            if not definition:
                definition = json.dumps(raw, ensure_ascii=False)
        elif isinstance(raw, list):
            definition = "\n".join(str(value) for value in raw).strip()
            summary = None
        else:
            definition = str(raw).strip()
            summary = None
        if not definition:
            return None
        first_line = definition.splitlines()[0].strip()
        return {
            "summary": str(summary or f"Precondition: {first_line[:77]}").strip(),
            "definition": definition,
        }

    @staticmethod
    def format_description(test: Dict[str, Any]) -> str:
        return str(test.get("description") or test.get("objective") or "").strip()

    @staticmethod
    def validate_test(test: Dict[str, Any], default_project: str, default_story: str) -> Dict[str, Any]:
        representation = _XrayTestFormatter.get_representation(test)
        if representation == "review":
            raise ValueError("test_representation review cannot be published")
        if representation not in ("manual", "cucumber"):
            raise ValueError("test_representation must be manual or cucumber")

        summary = str(test.get("summary") or test.get("title") or "").strip()
        if not summary:
            raise ValueError("Test is missing summary or title")

        project = str(default_project or test.get("project_key") or test.get("project") or "").strip()
        if not project:
            raise ValueError(f"Test '{summary}' is missing project_key")

        story = str(default_story or test.get("parent_feature_key") or test.get("story_key") or "").strip()
        normalized = {
            "source": test,
            "summary": summary,
            "description": _XrayTestFormatter.format_description(test),
            "representation": representation,
            "project": project,
            "story": story,
            "precondition": _XrayTestFormatter.extract_precondition(test),
        }
        if representation == "manual":
            normalized["steps"] = _XrayTestFormatter.format_steps(test.get("steps"))
            normalized["gherkin"] = None
        else:
            normalized["steps"] = None
            normalized["gherkin"] = _XrayTestFormatter.extract_gherkin(test)
        return normalized


class XrayJiraCompleteTraceabilityTool(BaseTool):
    name: str = "XrayJiraCompleteTraceabilityTool"
    description: str = (
        "Creates Manual or Cucumber Xray Tests and links them to a Jira Feature or Story"
    )
    args_schema: Type[BaseModel] = XrayJiraCompleteTraceabilitySchema

    def get_xray_token(self) -> str:
        response = requests.post(
            f"{xray_base_url}/api/v2/authenticate",
            json={"client_id": xray_client_id, "client_secret": xray_client_secret},
            verify=False,
            timeout=30,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Xray authentication failed HTTP {response.status_code}: {response.text}"
            )
        return response.text.strip('"')

    @staticmethod
    def _post_once(url: str, payload: Dict[str, Any], headers: Dict[str, str]) -> requests.Response:
        # Create mutations are intentionally not retried because a lost response can otherwise
        # create duplicate Jira/Xray issues.
        return requests.post(url, json=payload, headers=headers, verify=False, timeout=60)

    @staticmethod
    def _jira_link(source_key: str, target_key: str) -> str:
        response = requests.post(
            f"{jira_base_url}/rest/api/2/issueLink",
            json={
                "type": {"name": "Relates"},
                "inwardIssue": {"key": source_key},
                "outwardIssue": {"key": target_key},
            },
            auth=jira_auth,
            verify=False,
            timeout=30,
        )
        if response.status_code == 201:
            return f"Linked {source_key} to {target_key}"
        return f"Link failed HTTP {response.status_code}: {response.text}"

    def _run(self, project_key: str, story_key: str, tests_json: Any) -> str:
        try:
            raw_tests = _XrayTestFormatter.normalize_tests(tests_json)
            if not raw_tests:
                return json.dumps({"status": "failed", "error": "No valid tests found", "results": []})

            # Validate the full batch before creating anything. This prevents partial publication
            # caused by review or malformed cases.
            validated: List[Dict[str, Any]] = []
            validation_errors: List[Dict[str, Any]] = []
            for index, test in enumerate(raw_tests, start=1):
                try:
                    validated.append(
                        _XrayTestFormatter.validate_test(test, project_key, story_key)
                    )
                except Exception as exc:
                    validation_errors.append(
                        {
                            "index": index,
                            "test_case_id": test.get("test_case_id") if isinstance(test, dict) else None,
                            "error": str(exc),
                        }
                    )
            if validation_errors:
                return json.dumps(
                    {
                        "status": "failed",
                        "error": "Batch validation failed No tests were created",
                        "validation_errors": validation_errors,
                        "results": [],
                    },
                    ensure_ascii=False,
                )

            token = self.get_xray_token()
            gql_url = f"{xray_base_url}/api/v2/graphql"
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

            manual_mutation = """
            mutation CreateManualTest($projectKey: String!, $summary: String!, $desc: String!, $steps: [CreateStepInput]!) {
              createTest(
                testType: { name: "Manual" }
                steps: $steps
                jira: { fields: { project: { key: $projectKey }, summary: $summary, description: $desc } }
              ) {
                test { issueId jira(fields: ["key", "id"]) }
                warnings
              }
            }
            """

            cucumber_mutation = """
            mutation CreateCucumberTest($projectKey: String!, $summary: String!, $desc: String!, $gherkin: String!) {
              createTest(
                testType: { name: "Cucumber" }
                gherkin: $gherkin
                jira: { fields: { project: { key: $projectKey }, summary: $summary, description: $desc } }
              ) {
                test { issueId jira(fields: ["key", "id"]) }
                warnings
              }
            }
            """

            precondition_mutation = """
            mutation CreateManualPrecondition($projectKey: String!, $summary: String!, $desc: String!, $definition: String!) {
              createPrecondition(
                preconditionType: { name: "Manual" }
                definition: $definition
                jira: { fields: { project: { key: $projectKey }, summary: $summary, description: $desc } }
              ) {
                precondition { issueId jira(fields: ["key", "id"]) }
                warnings
              }
            }
            """

            link_precondition_mutation = """
            mutation LinkPreconditionToTest($testIssueId: String!, $preconditionIssueIds: [String]!) {
              addPreconditionsToTest(issueId: $testIssueId, preconditionIssueIds: $preconditionIssueIds) {
                addedPreconditions
                warning
              }
            }
            """

            results: List[Dict[str, Any]] = []
            precondition_cache: Dict[str, Dict[str, str]] = {}

            for test in validated:
                precondition_key = None
                precondition_id = None

                # Manual preconditions are created as separate Xray Precondition issues.
                # Cucumber starting state remains inside the approved Gherkin to avoid changing it.
                if test["representation"] == "manual" and test["precondition"]:
                    definition = test["precondition"]["definition"]
                    if definition in precondition_cache:
                        cached = precondition_cache[definition]
                        precondition_key = cached["key"]
                        precondition_id = cached["id"]
                    else:
                        variables = {
                            "projectKey": test["project"],
                            "summary": test["precondition"]["summary"],
                            "desc": definition,
                            "definition": definition,
                        }
                        response = self._post_once(
                            gql_url,
                            {"query": precondition_mutation, "variables": variables},
                            headers,
                        )
                        if response.status_code != 200:
                            results.append(
                                {
                                    "summary": test["summary"],
                                    "status": "failed",
                                    "stage": "create_precondition",
                                    "error": f"HTTP {response.status_code}: {response.text}",
                                }
                            )
                            continue
                        body = response.json()
                        if body.get("errors"):
                            results.append(
                                {
                                    "summary": test["summary"],
                                    "status": "failed",
                                    "stage": "create_precondition",
                                    "error": body["errors"],
                                }
                            )
                            continue
                        created = body.get("data", {}).get("createPrecondition", {}).get("precondition") or {}
                        jira = created.get("jira") or {}
                        precondition_key = jira.get("key")
                        precondition_id = created.get("issueId") or jira.get("id")
                        if not precondition_key:
                            results.append(
                                {
                                    "summary": test["summary"],
                                    "status": "failed",
                                    "stage": "create_precondition",
                                    "error": "Unexpected Xray response",
                                }
                            )
                            continue
                        precondition_cache[definition] = {
                            "key": str(precondition_key),
                            "id": str(precondition_id or precondition_key),
                        }

                if test["representation"] == "manual":
                    mutation = manual_mutation
                    variables = {
                        "projectKey": test["project"],
                        "summary": test["summary"],
                        "desc": test["description"],
                        "steps": test["steps"],
                    }
                    xray_type = "Manual"
                else:
                    mutation = cucumber_mutation
                    variables = {
                        "projectKey": test["project"],
                        "summary": test["summary"],
                        "desc": test["description"],
                        "gherkin": test["gherkin"],
                    }
                    xray_type = "Cucumber"

                response = self._post_once(
                    gql_url, {"query": mutation, "variables": variables}, headers
                )
                if response.status_code != 200:
                    results.append(
                        {
                            "summary": test["summary"],
                            "test_type": xray_type,
                            "status": "failed",
                            "stage": "create_test",
                            "error": f"HTTP {response.status_code}: {response.text}",
                        }
                    )
                    continue

                body = response.json()
                if body.get("errors"):
                    results.append(
                        {
                            "summary": test["summary"],
                            "test_type": xray_type,
                            "status": "failed",
                            "stage": "create_test",
                            "error": body["errors"],
                        }
                    )
                    continue

                created = body.get("data", {}).get("createTest", {}).get("test") or {}
                jira = created.get("jira") or {}
                test_key = jira.get("key")
                test_id = created.get("issueId") or jira.get("id")
                if not test_key:
                    results.append(
                        {
                            "summary": test["summary"],
                            "test_type": xray_type,
                            "status": "failed",
                            "stage": "create_test",
                            "error": "Unexpected Xray response",
                        }
                    )
                    continue

                precondition_link = None
                if precondition_key:
                    link_response = self._post_once(
                        gql_url,
                        {
                            "query": link_precondition_mutation,
                            "variables": {
                                "testIssueId": str(test_id or test_key),
                                "preconditionIssueIds": [str(precondition_id or precondition_key)],
                            },
                        },
                        headers,
                    )
                    if link_response.status_code == 200 and not link_response.json().get("errors"):
                        precondition_link = "linked"
                    else:
                        precondition_link = "failed"

                story_link = None
                if test["story"]:
                    story_link = self._jira_link(str(test_key), test["story"])

                results.append(
                    {
                        "summary": test["summary"],
                        "test_case_id": test["source"].get("test_case_id"),
                        "status": "created",
                        "test_key": test_key,
                        "test_type": xray_type,
                        "precondition_key": precondition_key,
                        "precondition_link": precondition_link,
                        "story_link": story_link,
                    }
                )

            created_count = sum(1 for item in results if item.get("status") == "created")
            failed_count = len(results) - created_count
            status = "success" if failed_count == 0 else ("partial" if created_count else "failed")
            return json.dumps(
                {
                    "status": status,
                    "created_count": created_count,
                    "failed_count": failed_count,
                    "results": results,
                },
                ensure_ascii=False,
            )
        except Exception as exc:
            return json.dumps(
                {"status": "failed", "error": str(exc), "results": []},
                ensure_ascii=False,
            )


XrayReader = XrayJiraCompleteTraceabilityTool
XrayJiraReader = XrayJiraCompleteTraceabilityTool
XrayWriter = XrayJiraCompleteTraceabilityTool
XrayJiraWriter = XrayJiraCompleteTraceabilityTool
