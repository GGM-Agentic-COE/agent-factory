import os
import re
import requests
from html.parser import HTMLParser
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


import json
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any


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
    SECRET_NAME: str = "aava/aava-atlassian-sa-dev-secret-asm"


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

# Secrets retrieved from AWS Secrets Manager
# SETUP-REQUIRED: these three key names must match the keys in the secret JSON
api_key = secrets.get("api_key")
user_email = secrets.get("id")
base_url = secrets.get("confluence_base_url")

# Fail loudly at startup rather than with a 401 on the first page read.
_missing = [k for k, v in
            (("api_key", api_key), ("user_email", user_email), ("base_url", base_url))
            if not v]
if _missing:
    raise RuntimeError(
        f"Secret '{AWSSecretReaderPodIdentity.SECRET_NAME}' is missing keys: {_missing}"
    )

# Trailing slash would produce '//rest/api/...' in the request URL.
base_url = base_url.strip().rstrip("/")

class ConfluencePageReaderSchema(BaseModel):
    """Input schema for ConfluencePageReader."""
    page_id: str = Field(..., description="The numeric ID of the Confluence page, e.g. '425985'.")


class _StorageToMarkdown(HTMLParser):
    """Converts Confluence storage-format XHTML to Markdown.

    Handles the ac:/ri: namespace that generic HTML converters drop:
    expand/code macro titles become headings and their bodies are kept.
    """

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0            # inside an ac:parameter we don't want
        self.in_pre = False
        self.pre_buf = []
        self.capture_title = False
        self.title_buf = []
        self.list_depth = 0
        self.rows = None         # buffered table rows
        self.row = None
        self.cell = None
        self.row_is_header = False

    # -- helpers ---------------------------------------------------------
    def _emit(self, text):
        self.out.append(text)

    def _sink(self):
        if self.in_pre:
            return self.pre_buf
        if self.capture_title:
            return self.title_buf
        if self.cell is not None:
            return self.cell
        return self.out

    # -- tags ------------------------------------------------------------
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)

        if tag == "ac:parameter":
            if (a.get("ac:name") or "") == "title":
                self.capture_title, self.title_buf = True, []
            else:
                self.skip += 1
            return
        if self.skip:
            return

        if tag in ("script", "style"):
            self.skip += 1
        elif tag == "pre":
            self.in_pre, self.pre_buf = True, []
        elif re.fullmatch(r"h[1-6]", tag):
            self._emit("\n\n" + "#" * int(tag[1]) + " ")
        elif tag in ("p", "div", "blockquote"):
            self._emit("\n\n")
        elif tag == "br":
            self._sink().append("  \n")
        elif tag in ("ul", "ol"):
            self.list_depth += 1
        elif tag == "li":
            self._emit("\n" + "  " * max(0, self.list_depth - 1) + "- ")
        elif tag == "table":
            self.rows = []
        elif tag == "tr":
            self.row, self.row_is_header = [], False
        elif tag in ("td", "th"):
            self.cell = []
            if tag == "th":
                self.row_is_header = True
        elif tag == "a":
            self._sink().append("[")
            self._href = a.get("href", "")
        elif tag in ("strong", "b"):
            self._sink().append("**")
        elif tag in ("em", "i"):
            self._sink().append("*")
        elif tag == "code":
            self._sink().append("`")

    def handle_endtag(self, tag):
        if tag == "ac:parameter":
            if self.capture_title:
                title = "".join(self.title_buf).strip()
                self.capture_title = False
                if title:
                    self._emit(f"\n\n### {title}\n\n")
            elif self.skip:
                self.skip -= 1
            return
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return

        if tag == "pre":
            self.in_pre = False
            body = "".join(self.pre_buf).strip()
            if body:
                # Pages built by publishing .txt/.md/.yaml files have <pre>
                # blocks that are ALREADY Markdown (mermaid fences, pipe
                # tables). Re-fencing would nest code blocks.
                already_md = (
                    "```" in body
                    or re.search(r"^\s*\|.*\|\s*$", body, re.M)
                    or re.search(r"^\s*#{1,6}\s+\S", body, re.M)
                )
                self._emit(f"\n\n{body}\n\n" if already_md
                           else f"\n\n```\n{body}\n```\n\n")
        elif re.fullmatch(r"h[1-6]", tag):
            self._emit("\n\n")
        elif tag in ("p", "div", "blockquote"):
            self._emit("\n\n")
        elif tag in ("ul", "ol"):
            self.list_depth = max(0, self.list_depth - 1)
            self._emit("\n")
        elif tag in ("td", "th"):
            if self.row is not None and self.cell is not None:
                text = re.sub(r"\s+", " ", "".join(self.cell)).strip()
                self.row.append(text)
            self.cell = None
        elif tag == "tr":
            if self.rows is not None and self.row:
                self.rows.append((self.row_is_header, self.row))
            self.row = None
        elif tag == "table":
            self._emit(self._render_table())
            self.rows = None
        elif tag == "a":
            self._sink().append(f"]({getattr(self, '_href', '')})")
        elif tag in ("strong", "b"):
            self._sink().append("**")
        elif tag in ("em", "i"):
            self._sink().append("*")
        elif tag == "code":
            self._sink().append("`")

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_pre:
            self.pre_buf.append(data)
        else:
            self._sink().append(data)

    # -- table -----------------------------------------------------------
    def _render_table(self):
        if not self.rows:
            return ""
        width = max(len(cells) for _, cells in self.rows)
        header, body = None, list(self.rows)
        if body and body[0][0]:
            header = body.pop(0)[1]
        else:
            header = [""] * width

        def line(cells):
            cells = list(cells) + [""] * (width - len(cells))
            return "| " + " | ".join(cells) + " |"

        lines = [line(header), "| " + " | ".join(["---"] * width) + " |"]
        lines += [line(cells) for _, cells in body]
        return "\n\n" + "\n".join(lines) + "\n\n"

    def result(self):
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


class ConfluencePageReader(BaseTool):
    """Reads the contents of a Confluence page via the REST API, as Markdown."""
    name: str = "Confluence Page Reader"
    description: str = "Reads a specified Confluence page and returns its contents as Markdown."
    args_schema: Type[BaseModel] = ConfluencePageReaderSchema

    max_chars: int = 80_000

    def _run(self, page_id: str) -> str:

        url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}?expand=body.storage"
        headers = {"Accept": "application/json"}
        auth = (user_email, api_key)

        try:
            response = requests.get(url, headers=headers, auth=auth, timeout=30)
            response.raise_for_status()
            data = response.json()
            content = data.get("body", {}).get("storage", {}).get("value", "")
            title = data.get("title", "")
        except requests.RequestException as e:
            return f"Error reading Confluence page: {str(e)}"

        if not content.strip():
            return f"# {title}\n\nurl{base_url}\n\n_(Page {page_id} has an empty body.)_"

        try:
            parser = _StorageToMarkdown()
            parser.feed(content)
            parser.close()
            markdown = parser.result()
        except Exception as e:
            return f"Error converting page to Markdown: {type(e).__name__}: {e}"

        if len(markdown) > self.max_chars:
            markdown = markdown[: self.max_chars] + "\n\n_[Truncated.]_"

        return f"# {title}\n \n {markdown}"