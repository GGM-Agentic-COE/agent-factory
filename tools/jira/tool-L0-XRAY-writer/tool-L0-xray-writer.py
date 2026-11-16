import os
import re
import json
import urllib3
import requests
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import boto3
from botocore.exceptions import ClientError

# Suppress SSL warnings for local execution
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity."""
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
    SECRET_NAME: str = "aava-secret-manager-sfi-credentials"

    def _run(self) -> Dict[str, Any]:
        try:
            # SETUP-REQUIRED: AWS region where that secret lives (us-east-1 or us-east-2 depending on deployment)
            client = boto3.client('secretsmanager', region_name='us-east-2')
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

# Secrets retrieved from AWS Secrets Manager
# SETUP-REQUIRED: these key names must match the keys in the secret JSON
api_key = secrets.get("api_key")
user_email = secrets.get("id")
jira_base_url = secrets.get("base_url") or secrets.get("jira_base_url")
xray_client_id = secrets.get("xray_client_id")
xray_client_secret = secrets.get("xray_client_secret")
xray_base_url = (secrets.get("xray_base_url") or "https://eu.xray.cloud.getxray.app").strip().rstrip("/")

jira_user = user_email
jira_api_token = api_key

# Fail loudly at startup rather than during execution.
_missing = [k for k, v in
            (("api_key", api_key), ("user_email", user_email), ("jira_base_url", jira_base_url),
             ("xray_client_id", xray_client_id), ("xray_client_secret", xray_client_secret))
            if not v]
if _missing:
    raise RuntimeError(
        f"Secret '{AWSSecretReaderPodIdentity.SECRET_NAME}' is missing keys: {_missing}"
    )

# Trailing slash would produce '//rest/api/...' in the request URL.
jira_base_url = jira_base_url.strip().rstrip("/")
if not jira_base_url.startswith(("http://", "https://")):
    jira_base_url = f"https://{jira_base_url}"


class XrayJiraCompleteTraceabilitySchema(BaseModel):
    """Input schema for XrayJiraCompleteTraceabilityTool."""
    project_key: str = Field(default="", description="Target Jira Project Key, e.g. 'PROJ'.")
    story_key: str = Field(default="", description="Target Jira Story Key to link tests to, e.g. 'PROJ-123'.")
    tests_json: Any = Field(default="[]", description="JSON string, dict, or list containing test cases.")


class _XrayTestFormatter:
    """Helper class to format and normalize test cases and steps for Xray GraphQL."""

    @staticmethod
    def normalize_tests(tests_data: Any) -> List[Dict[str, Any]]:
        """Safely parses and normalizes input tests into a list of dictionaries."""
        data = tests_data

        # If it's a string, try parsing as JSON (handles single or double encoding)
        if isinstance(data, str):
            data = data.strip()
            try:
                data = json.loads(data)
            except Exception:
                pass

        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                pass

        # If an envelope dict is passed, extract the test list
        if isinstance(data, dict):
            for key in ("tests", "scenarios", "test_cases", "data"):
                if key in data and isinstance(data[key], (list, dict)):
                    data = data[key]
                    break

        # If a single test dictionary was provided, wrap it in a list
        if isinstance(data, dict):
            return [data]

        # If it is a list, normalize each item
        if isinstance(data, list):
            normalized = []
            for item in data:
                if isinstance(item, dict):
                    normalized.append(item)
                elif isinstance(item, str):
                    try:
                        parsed = json.loads(item)
                        if isinstance(parsed, dict):
                            normalized.append(parsed)
                        else:
                            normalized.append({"summary": str(item)})
                    except Exception:
                        normalized.append({"summary": str(item)})
            return normalized

        return []

    @staticmethod
    def format_steps(raw_steps: Any, test: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Normalizes and formats test steps for Xray CreateStepInput."""
        if isinstance(raw_steps, str):
            try:
                raw_steps = json.loads(raw_steps)
            except Exception:
                raw_steps = [{"action": raw_steps, "data": "", "expected_result": ""}]

        if isinstance(raw_steps, dict):
            raw_steps = [raw_steps]
        elif not isinstance(raw_steps, list):
            raw_steps = []

        formatted_steps = []
        for step in raw_steps:
            if isinstance(step, str):
                step = {"action": step}
            elif not isinstance(step, dict):
                continue

            action = step.get("action", "")
            data = step.get("data") or step.get("test_data", "")
            result = step.get("expected_result", step.get("result", ""))

            if action or data or result:
                formatted_steps.append({
                    "action": str(action),
                    "data": str(data),
                    "result": str(result)
                })

        # Fallback to test navigable_path / expected_result if present
        if not formatted_steps and test:
            action = test.get("navigable_path", "")
            result = test.get("expected_result", "")
            data = test.get("test_data", "")
            if action or result:
                formatted_steps.append({
                    "action": str(action or "Execute test according to description"),
                    "data": str(data or ""),
                    "result": str(result or "Expected behavior is observed")
                })

        # Final fallback if no steps are present
        if not formatted_steps:
            formatted_steps.append({
                "action": "Execute test according to description",
                "data": "",
                "result": "Expected behavior is observed"
            })
        return formatted_steps

    @staticmethod
    def extract_precondition(test: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Extracts precondition summary and definition if present in test."""
        raw_precond = test.get("pre_condition") or test.get("precondition") or test.get("preconditions")
        if not raw_precond:
            return None

        if isinstance(raw_precond, dict):
            summary = raw_precond.get("summary") or raw_precond.get("title")
            definition = raw_precond.get("definition") or raw_precond.get("description") or str(raw_precond)
            if not summary:
                summary = f"Precondition: {str(definition)[:60]}"
            return {"summary": str(summary).strip(), "definition": str(definition).strip()}

        if isinstance(raw_precond, list):
            definition = "\n".join(str(p) for p in raw_precond).strip()
        else:
            definition = str(raw_precond).strip()

        if not definition:
            return None

        first_line = definition.split("\n")[0].strip()
        if len(first_line) <= 80:
            summary = f"Precondition: {first_line}"
        else:
            summary = f"Precondition: {first_line[:77]}..."

        return {"summary": summary, "definition": definition}

    @staticmethod
    def format_description(test: Dict[str, Any]) -> str:
        """Extracts and formats description with manual steps reference if present."""
        if not isinstance(test, dict):
            return str(test)
        test_desc = test.get("description") or test.get("test_scenario_description") or ""
        # Add Manual Steps to Test description (legacy fallback)
        if "manualsteps" in test:
            test_desc += "\n\n*Manual Steps Reference:*\n" + str(test["manualsteps"])
        return test_desc.strip()


class XrayJiraCompleteTraceabilityTool(BaseTool):
    """Creates Tests with steps, sets Test Type, and links them natively to a Jira Story."""
    name: str = "XrayJiraCompleteTraceabilityTool"
    description: str = "Creates Tests with steps, sets Test Type, and links them natively to a Jira Story."
    args_schema: Type[BaseModel] = XrayJiraCompleteTraceabilitySchema

    def get_xray_token(self, client_id: str, client_secret: str) -> str:
        """Authenticates with Xray API using provided client credentials."""
        url = f"{xray_base_url}/api/v2/authenticate"
        resp = requests.post(
            url,
            json={"client_id": client_id, "client_secret": client_secret},
            verify=False
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Xray authentication failed (HTTP {resp.status_code}): {resp.text}")
        return resp.text.strip('"')

    def link_work_item(self, target_jira_base_url: str, source_key: str, target_key: str, jira_auth: tuple, link_type: str = "Relates") -> str:
        """Natively links two Jira issues together so they appear in the 'Linked work items' UI."""
        link_url = f"{target_jira_base_url}/rest/api/2/issueLink"
        link_payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": source_key},
            "outwardIssue": {"key": target_key}
        }
        res = requests.post(link_url, json=link_payload, auth=jira_auth, verify=False)

        if res.status_code == 201:
            return f"✅ Linked work item: {source_key} -> {target_key}"
        else:
            return f"⚠️ Work item link failed (HTTP {res.status_code}): {res.text}"

    def _post_graphql_with_retry(self, gql_url: str, payload: Dict[str, Any], headers: Dict[str, str], max_retries: int = 3) -> requests.Response:
        """Sends GraphQL request to Xray with automatic retry on transient gateway errors (502, 503, 504, 429)."""
        import time
        resp = None
        for attempt in range(max_retries):
            resp = requests.post(gql_url, json=payload, headers=headers, verify=False)
            if resp.status_code not in (502, 503, 504, 429):
                return resp
            # Wait with backoff before retrying transient gateway hiccup
            time.sleep(1.5 * (attempt + 1))
        return resp

    def _run(self, project_key: str, story_key: str, tests_json: Any) -> str:
        try:
            xray_token = self.get_xray_token(xray_client_id, xray_client_secret)
            gql_url = f"{xray_base_url}/api/v2/graphql"
            headers = {"Authorization": f"Bearer {xray_token}", "Content-Type": "application/json"}
            jira_auth = (jira_user, jira_api_token)

            tests = _XrayTestFormatter.normalize_tests(tests_json)
            if not tests:
                return "❌ No valid tests found in input."

            results = []
            precondition_cache: Dict[str, Dict[str, str]] = {}

            # GraphQL Mutations for Xray Cloud
            test_mutation = """
            mutation CreateTestIssue($projectKey: String!, $summary: String!, $desc: String!, $testType: String!, $steps: [CreateStepInput]!) {
              createTest(
                testType: { name: $testType },
                steps: $steps,
                jira: { fields: { project: { key: $projectKey }, summary: $summary, description: $desc } }
              ) {
                test {
                  issueId
                  jira(fields: ["key", "id"])
                }
              }
            }
            """

            precond_mutation = """
            mutation CreatePreconditionIssue($projectKey: String!, $summary: String!, $desc: String!, $precondType: String!, $definition: String!) {
              createPrecondition(
                preconditionType: { name: $precondType },
                definition: $definition,
                jira: { fields: { project: { key: $projectKey }, summary: $summary, description: $desc } }
              ) {
                precondition {
                  issueId
                  jira(fields: ["key", "id"])
                }
              }
            }
            """

            link_precond_mutation = """
            mutation LinkPreconditionToTest($testIssueId: String!, $precondIssueIds: [String]!) {
              addPreconditionsToTest(
                issueId: $testIssueId,
                preconditionIssueIds: $precondIssueIds
              ) {
                addedPreconditions
                warning
              }
            }
            """

            for test in tests:
                # ---------------------------------------------------------
                # DATA PRESERVATION AND PARSING
                # ---------------------------------------------------------
                raw_summary = (
                    test.get("summary")
                    or test.get("test_scenario_id")
                    or test.get("test_scenario_description")
                    or "Untitled Test"
                )
                test_desc = _XrayTestFormatter.format_description(test)

                # In Xray Cloud, tests with steps must be 'Manual'
                raw_type = test.get("test_type", "Manual")
                test_type = "Manual" if str(raw_type).strip().lower() in ("functional", "manual", "") else str(raw_type)

                target_project = project_key or test.get("project") or test.get("project_key") or ""
                target_story = story_key or test.get("parent_feature_key") or test.get("story_key") or ""

                formatted_steps = _XrayTestFormatter.format_steps(test.get("steps", []), test=test)

                # ==========================================
                # 1. CREATE PRECONDITION IN XRAY (if present)
                # ==========================================
                precond_info = _XrayTestFormatter.extract_precondition(test)
                precond_key = None
                precond_id = None

                if precond_info:
                    p_def = precond_info["definition"]
                    p_sum = precond_info["summary"]

                    # Deduplicate across test cases
                    if p_def in precondition_cache:
                        cached = precondition_cache[p_def]
                        precond_key = cached.get("key")
                        precond_id = cached.get("id")
                    else:
                        p_vars = {
                            "projectKey": target_project,
                            "summary": p_sum,
                            "desc": p_def,
                            "precondType": "Manual",
                            "definition": p_def
                        }
                        p_resp = self._post_graphql_with_retry(gql_url, {"query": precond_mutation, "variables": p_vars}, headers=headers)
                        if p_resp.status_code == 200:
                            try:
                                p_json = p_resp.json()
                                if "errors" in p_json:
                                    results.append(f"⚠️ Error creating Precondition: {json.dumps(p_json['errors'])}")
                                else:
                                    p_data = p_json.get("data", {}).get("createPrecondition", {}).get("precondition", {})
                                    if p_data and "jira" in p_data:
                                        precond_key = p_data["jira"]["key"]
                                        precond_id = p_data.get("issueId") or p_data["jira"].get("id")
                                        precondition_cache[p_def] = {"key": precond_key, "id": precond_id}
                                        results.append(f"✅ Created Xray Precondition {precond_key}: {p_sum}")
                            except Exception as ex:
                                results.append(f"⚠️ Failed to parse Precondition response: {str(ex)}")
                        else:
                            results.append(f"⚠️ HTTP {p_resp.status_code} creating Precondition: {p_resp.text}")

                # ==========================================
                # 2. CREATE TEST WITH STEPS (GraphQL)
                # ==========================================
                t_vars = {
                    "projectKey": target_project,
                    "summary": raw_summary,
                    "desc": test_desc,
                    "testType": test_type,
                    "steps": formatted_steps
                }
                t_resp = self._post_graphql_with_retry(gql_url, {"query": test_mutation, "variables": t_vars}, headers=headers)

                if t_resp.status_code != 200:
                    results.append(f"❌ HTTP {t_resp.status_code} creating Test: {t_resp.text}")
                    continue

                try:
                    t_json = t_resp.json()
                except Exception:
                    results.append(f"❌ Failed to parse response (HTTP {t_resp.status_code}): {t_resp.text}")
                    continue

                if "errors" in t_json:
                    results.append(f"❌ Error creating Test: {json.dumps(t_json['errors'])}")
                    continue

                t_data = t_json.get("data", {}).get("createTest", {}).get("test", {})
                if not t_data or "jira" not in t_data:
                    results.append(f"❌ Error: Unexpected response format: {json.dumps(t_json)}")
                    continue

                test_key = t_data["jira"]["key"]
                test_id = t_data.get("issueId") or t_data["jira"].get("id")

                # ==========================================
                # 3. LINK PRECONDITION TO TEST (GraphQL)
                # ==========================================
                if precond_key and (precond_id or precond_key) and (test_id or test_key):
                    target_test_id = str(test_id) if test_id else str(test_key)
                    target_precond_id = str(precond_id) if precond_id else str(precond_key)

                    link_vars = {
                        "testIssueId": target_test_id,
                        "precondIssueIds": [target_precond_id]
                    }
                    l_resp = self._post_graphql_with_retry(gql_url, {"query": link_precond_mutation, "variables": link_vars}, headers=headers)
                    if l_resp.status_code == 200:
                        try:
                            l_json = l_resp.json()
                            if "errors" in l_json:
                                results.append(f"⚠️ Failed to link Precondition {precond_key} to Test {test_key}: {json.dumps(l_json['errors'])}")
                            else:
                                results.append(f"🔗 Associated Precondition {precond_key} -> Test {test_key}")
                        except Exception:
                            results.append(f"🔗 Associated Precondition {precond_key} -> Test {test_key}")
                    else:
                        results.append(f"⚠️ HTTP {l_resp.status_code} linking Precondition {precond_key} to Test {test_key}: {l_resp.text}")

                # ==========================================
                # 4. LINK USER STORY TO TESTS (Jira Native REST)
                # ==========================================
                if target_story:
                    link_url = f"{jira_base_url}/rest/api/2/issueLink"
                    link_payload = {
                        "type": {"name": "Relates"},
                        "inwardIssue": {"key": test_key},
                        "outwardIssue": {"key": target_story}
                    }
                    link_res = requests.post(link_url, json=link_payload, auth=jira_auth, verify=False)

                    if link_res.status_code == 201:
                        results.append(f"✅ Created Test {test_key} (Type: {test_type}). Linked successfully to Story {target_story}.")
                    else:
                        results.append(f"✅ Created Test {test_key} (Type: {test_type}), but Story Link failed (HTTP {link_res.status_code}): {link_res.text}")
                else:
                    results.append(f"✅ Created Test {test_key} (Type: {test_type}).")

            return "\n".join(results)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"❌ System Error: {str(e)}"


# Aliases for convenience matching folder or file naming conventions
XrayReader = XrayJiraCompleteTraceabilityTool
XrayJiraReader = XrayJiraCompleteTraceabilityTool
XrayWriter = XrayJiraCompleteTraceabilityTool
XrayJiraWriter = XrayJiraCompleteTraceabilityTool
