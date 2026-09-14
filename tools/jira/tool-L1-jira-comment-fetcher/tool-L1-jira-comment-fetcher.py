import os
import requests
from typing import Any, Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth
import urllib3

# Disable SSL warnings (only when JIRA_VERIFY_SSL=false, i.e. local dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JIRACommentFetcherSchema(BaseModel):
    '''Input schema for JIRACommentFetcher.'''
    issue_key: str = Field(..., description="JIRA issue key (e.g., PROJECT-123)")
    max_results: Optional[int] = Field(
        default=50,
        description="Maximum number of comments to return (default 50, max 1000)."
    )
    order_by: Optional[str] = Field(
        default="created",
        description="Sort order for comments. Use 'created' for ascending (oldest first) or '-created' for descending (newest first)."
    )


class JIRACommentFetcher(BaseTool):
    '''
    JIRACommentFetcher - A tool to retrieve all comments from a JIRA issue via API.

    Companion to JIRACommentPublisher. Used by agents that need to read the
    existing comment thread on a ticket — for example, to understand prior
    review notes, audit entries, or decisions recorded by other agents before
    posting a new comment or making a verdict.

    Returns a structured list of comments including author, timestamp, and body.
    '''

    name: str = "JIRA Comment Fetcher"
    description: str = "A tool to fetch all comments from a JIRA issue."
    args_schema: Type[BaseModel] = JIRACommentFetcherSchema
    jira_url: str = "https://worktejasc.atlassian.net"

    def _run(self, issue_key: str, max_results: int = 50, order_by: str = "created") -> Any:
        try:
            print(f"Fetching comments from JIRA issue: {issue_key}")

            # Retrieve API token and username from secret manager / environment.
            # Never hardcode credentials in the tool body.
            username = "work.tejasc@gmail.com"
            api_token = '[REDACTED]'
            if not username or not api_token:
                return {
                    "success": False,
                    "error": "Missing credentials. Set JIRA_USERNAME and JIRA_API_TOKEN."
                }

            # Construct the API endpoint URL
            self.jira_url = "https://worktejasc.atlassian.net"
            api_endpoint = f"{self.jira_url.rstrip('/')}/rest/api/2/issue/{issue_key}/comment"

            # Set up the authentication
            auth = HTTPBasicAuth(username, api_token)

            # Set headers
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            # Query parameters for pagination and ordering
            params = {
                "maxResults": min(max_results, 1000),
                "orderBy": order_by,
            }

            verify_ssl = os.environ.get("JIRA_VERIFY_SSL", "true").lower() != "false"

            response = requests.get(
                api_endpoint,
                headers=headers,
                auth=auth,
                params=params,
                verify=verify_ssl,
                timeout=30
            )

            # Surface JIRA's own error messages rather than a bare status code
            if response.status_code >= 400:
                detail = response.text
                try:
                    err = response.json()
                    detail = "; ".join(
                        err.get("errorMessages", []) +
                        [f"{k}: {v}" for k, v in err.get("errors", {}).items()]
                    ) or response.text
                except ValueError:
                    pass
                return {
                    "success": False,
                    "issue_key": issue_key,
                    "status_code": response.status_code,
                    "error": f"Error fetching comments: {detail}"
                }

            data = response.json()
            raw_comments = data.get("comments", [])
            total = data.get("total", len(raw_comments))

            # Normalise each comment into a clean dict for downstream agents
            comments = []
            for c in raw_comments:
                author = c.get("author") or {}
                update_author = c.get("updateAuthor") or {}
                comments.append({
                    "comment_id": c.get("id"),
                    "comment_url": f"{self.jira_url.rstrip('/')}/browse/{issue_key}?focusedCommentId={c.get('id')}",
                    "author": author.get("displayName"),
                    "author_email": author.get("emailAddress"),
                    "created": c.get("created"),
                    "updated": c.get("updated"),
                    "update_author": update_author.get("displayName"),
                    "body": c.get("body", ""),
                })

            return {
                "success": True,
                "issue_key": issue_key,
                "total_comments": total,
                "returned_comments": len(comments),
                "comments": comments,
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "issue_key": issue_key,
                "error": f"Error fetching comments: {str(e)}"
            }
