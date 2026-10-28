import os
import re
import requests
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
    SECRET_NAME: str = "<name-of-secret-in-aws-secrets-manager>"


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


secrets = AWSSecretReaderPodIdentity()._run()

# Secrets retrieved from AWS Secrets Manager
# SETUP-REQUIRED: these three key names must match the keys in the secret JSON
api_key = secrets.get("api_key")
user_email = secrets.get("id")
base_url = secrets.get("confluence_base_url")


_LINK_START = "<a " + "hr" + "ef=" + '"'
_CDATA_OPEN = "<!" + "[CDATA["
_CDATA_CLOSE = "]]" + ">"
_CODE_LANGUAGES = {
    "python": "python", "py": "python",
    "java": "java",
    "javascript": "javascript", "js": "javascript", "jsx": "javascript", "node": "javascript",
    "typescript": "typescript", "ts": "typescript", "tsx": "typescript",
    "bash": "bash", "sh": "bash", "shell": "bash", "zsh": "bash", "console": "bash",
    "sql": "sql",
    "json": "json",
    "yaml": "yaml", "yml": "yaml",
    "xml": "xml", "html": "html",
    "css": "css",
    "go": "go", "golang": "go",
    "kotlin": "kotlin", "kt": "kotlin",
    "scala": "scala",
    "groovy": "groovy",
    "ruby": "ruby", "rb": "ruby",
    "php": "php",
    "cpp": "cpp", "c++": "cpp",
    "powershell": "powershell", "ps1": "powershell",
    "perl": "perl",
    "diff": "diff",
    "csharp": "csharp", "cs": "csharp", "c#": "csharp",
    "c": "cpp", "h": "cpp",
}


def _code_block(lines, language):
    """Render a fenced code block as a Confluence code macro with syntax highlighting."""
    code = "\n".join(lines).strip("\n").replace(_CDATA_CLOSE, "]]" + _CDATA_CLOSE + _CDATA_OPEN + ">")
    language = _CODE_LANGUAGES.get(language.lower(), "")
    param = '<ac:parameter ac:name="language">' + language + "</ac:parameter>" if language else ""
    return (
        '<ac:structured-macro ac:name="code">' + param
        + "<ac:plain-text-body>" + _CDATA_OPEN + code + _CDATA_CLOSE + "</ac:plain-text-body>"
        + "</ac:structured-macro>"
    )


def _esc(text):
    """Escape text for Confluence storage format."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _hide_escape(match):
    return "@@ESC" + str(ord(match.group(1))) + "@@"


def _show_escape(match):
    return _esc(chr(int(match.group(1))))


def _show_escape_raw(match):
    return "\\" + chr(int(match.group(1)))


def _inline(text):
    """Convert inline Markdown (code, links, bold, italic) to storage format."""
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!|>~])", _hide_escape, text)
    out = []
    for part in re.split(r"(```.+?```|``.+?``|`[^`]+`)", text):
        if len(part) > 1 and part.startswith("`") and part.endswith("`"):
            code = re.sub(r"@@ESC(\d+)@@", _show_escape_raw, part.strip("`").strip())
            out.append("<code>" + _esc(code) + "</code>")
        else:
            p = _esc(part)
            p = re.sub(r"\[([^\]]+)\]\(([^)\s\"]+)\)", _LINK_START + r'\2">\1</a>', p)
            p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
            p = re.sub(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])", r"<em>\1</em>", p)
            out.append(re.sub(r"@@ESC(\d+)@@", _show_escape, p))
    return "".join(out)


def _table(rows):
    """Convert Markdown table rows to a storage-format table. The first row is the header."""
    html_rows = []
    for n, row in enumerate(rows):
        tag = "th" if n == 0 else "td"
        row = row.strip()
        row = row[1:] if row.startswith("|") else row
        row = row[:-1] if row.endswith("|") and not row.endswith("\\|") else row
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", row)]
        html_rows.append("<tr>" + "".join("<" + tag + "><p>" + _inline(c) + "</p></" + tag + ">" for c in cells) + "</tr>")
    return "<table><tbody>" + "".join(html_rows) + "</tbody></table>"


def _flush(out, st):
    """Write any pending paragraph, list or table to the output."""
    if st["para"]:
        out.append("<p>" + _inline(" ".join(st["para"])) + "</p>")
    if st["items"]:
        items = ""
        for text, subs in st["items"]:
            sub_html = "".join("<li>" + _inline(x) + "</li>" for x in subs)
            items += "<li>" + _inline(text) + ("<ul>" + sub_html + "</ul>" if subs else "") + "</li>"
        out.append("<" + st["tag"] + ">" + items + "</" + st["tag"] + ">")
    if st["table"]:
        out.append(_table(st["table"]))
    st["para"], st["items"], st["table"] = [], [], []


def md_to_storage(md):
    """Convert Markdown to Confluence storage format. Storage-format input is returned unchanged."""
    md = md or ""
    if re.match(r"\s*<(p|h[1-6]|table|ul|ol|div|pre)\b", md):
        return md
    wrapped = re.match(r"^\s*```(?:markdown|md)\s*\n(.*)\n\s*```\s*$", md, re.S)
    if wrapped:
        md = wrapped.group(1)

    lines = md.replace("\r\n", "\n").split("\n")
    out, code = [], None
    fence, language, indent, code_start = "", "", 0, 0
    st = {"para": [], "items": [], "table": [], "tag": "ul"}
    for n, line in enumerate(lines):
        s = line.strip()
        if code is not None:
            if s and set(s) == {fence[0]} and len(s) >= len(fence):
                out.append(_code_block(code, language))
                code = None
                continue
            reopened = re.match(r"^(`{3,}|~{3,})([\w+#.-]+)$", s)
            if reopened and reopened.group(1) == fence and reopened.group(2).lower() in _CODE_LANGUAGES:
                out.append(_code_block(code, language))
                code, code_start = [], n
                fence, language = reopened.group(1), reopened.group(2)
                indent = len(line) - len(line.lstrip())
                continue
            strip = min(indent, len(line) - len(line.lstrip()))
            if s.endswith(fence) and len(s) > len(fence):
                code.append(line[strip:].rstrip()[:-len(fence)].rstrip())
                out.append(_code_block(code, language))
                code = None
                continue
            code.append(line[strip:])
            continue
        opening = re.match(r"^(`{3,}|~{3,})(.*)$", s)
        if opening:
            _flush(out, st)
            fence, rest = opening.group(1), opening.group(2).strip()
            if rest.endswith(fence):
                inner = rest[:-len(fence)].strip()
                one_line = re.match(r"^([\w+#.-]+)\s+(.+)$", inner)
                if one_line and one_line.group(1).lower() in _CODE_LANGUAGES:
                    out.append(_code_block([one_line.group(2)], one_line.group(1)))
                else:
                    out.append(_code_block([inner], ""))
                continue
            language, first = rest, ""
            if not re.match(r"^[\w+#.-]*$", rest):
                language, first = "", rest
            code, code_start = ([first] if first else []), n
            indent = len(line) - len(line.lstrip())
            continue
        if not s:
            _flush(out, st)
            continue
        if s.startswith("|"):
            if not st["table"]:
                _flush(out, st)
            if not re.match(r"^[\s:|-]+$", s):
                st["table"].append(s)
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", s)
        if heading:
            _flush(out, st)
            level = str(len(heading.group(1)))
            out.append("<h" + level + ">" + _inline(heading.group(2).rstrip("#").strip()) + "</h" + level + ">")
            continue
        if re.match(r"^([-*_])(\s*\1){2,}$", s):
            _flush(out, st)
            out.append("<hr />")
            continue
        item = re.match(r"^([-*+]|\d+[.)])\s+(.*)$", s)
        if item and st["items"] and line[:1].isspace():
            st["items"][-1][1].append(item.group(2))
            continue
        if item:
            tag = "ol" if item.group(1)[0].isdigit() else "ul"
            if st["para"] or st["table"] or (st["items"] and st["tag"] != tag):
                _flush(out, st)
            st["tag"] = tag
            st["items"].append([item.group(2), []])
            continue
        if st["items"] and line[:1].isspace():
            last = st["items"][-1]
            if last[1]:
                last[1][-1] += " " + s
            else:
                last[0] += " " + s
            continue
        if st["items"] or st["table"]:
            _flush(out, st)
        st["para"].append(s.lstrip(">").strip())
    if code is not None:
        cut = len(code)
        for i, code_line in enumerate(code):
            if re.match(r"^#{2,6}\s+\S", code_line.strip()):
                cut = i
                break
        out.append(_code_block(code[:cut], language))
        if cut < len(code):
            _flush(out, st)
            out.append(md_to_storage("\n".join(lines[code_start + 1 + cut:])))
            return "".join(out)
    _flush(out, st)
    return "".join(out)


_TIMEOUT = 30


def _page_link(response_data, fallback_base, webui):
    """Build a browser link, preferring the site address Confluence returns over the API address."""
    if not webui:
        return "(link unavailable)"
    site = response_data.get("_links", {}).get("base") or fallback_base
    return site.rstrip("/") + webui


def _space_of_content(api, headers, auth, content_id):
    """Return the space key of a page or folder ID using v1 endpoints only, or None if not found."""
    by_id = requests.get(
        f"{api}/rest/api/content/{content_id}",
        headers=headers, auth=auth, params={"expand": "space"}, timeout=_TIMEOUT,
    )
    if by_id.status_code == 200:
        key = by_id.json().get("space", {}).get("key")
        if key:
            return key
    elif by_id.status_code not in (400, 404):
        by_id.raise_for_status()

    by_cql = requests.get(
        f"{api}/rest/api/content/search",
        headers=headers, auth=auth, params={"cql": f"id={content_id}", "expand": "space"}, timeout=_TIMEOUT,
    )
    if by_cql.status_code == 200:
        for item in by_cql.json().get("results", []):
            key = item.get("space", {}).get("key")
            if key:
                return key
    elif by_cql.status_code not in (400, 404):
        by_cql.raise_for_status()
    return None


def _resolve_target(api, headers, auth, target):
    """
    Resolve the target into (space_key, folder_id).

        "ENG"            -> ("ENG", None)          root of the space
        "ENG/123456789"  -> ("ENG", "123456789")   inside that folder, no lookup needed
        "123456789"      -> ("ENG", "123456789")   folder ID, space looked up via v1
    A numeric value that matches no content is treated as a numeric space key.
    """
    target = target.strip()
    explicit = re.match(r"^([^/\s]+)/(\d+)$", target)
    if explicit:
        return explicit.group(1), explicit.group(2)
    if not target.isdigit():
        return target, None
    space_key = _space_of_content(api, headers, auth, target)
    if space_key:
        return space_key, target
    return target, None


def _explain(status):
    """Add a hint for common authorisation failures."""
    if status == 401:
        return ("\nHint: 401 means the token was rejected. Check the email, the API token, and that "
                "confluence_base_url is the api.atlassian.com/ex/confluence/<cloudId>/wiki address.")
    if status == 403:
        return ("\nHint: 403 means a missing scope or Confluence permission. This tool needs "
                "write:confluence-content plus classic read scopes (read:confluence-content.all, "
                "read:confluence-space.summary), and space permission to add pages.")
    return ""


class ConfluenceScopedPageCreatorSchema(BaseModel):
    """Input schema for ConfluenceScopedPageCreator."""
    title: str = Field(..., description="The title of the Confluence page. If it exists, content is appended; otherwise a new page is created.")
    content: str = Field(..., description="The body content to add, in Markdown (headings, tables, lists, code fences, links). It is converted to Confluence format automatically. Confluence storage-format XHTML is also accepted and passed through unchanged.")
    space_key: str = Field(..., description="Where to write. A space key (e.g. 'ENG') writes at the root of the space. A folder ID (e.g. '123456789') or 'SPACEKEY/folderID' (e.g. 'ENG/123456789') writes inside that folder.")


class ConfluenceScopedPageCreator(BaseTool):
    """Creates or appends to a Confluence page using only v1 endpoints and classic scopes."""
    name: str = "Confluence Page Creator (Scoped Token)"
    description: str = "Creates a new Confluence page from Markdown content, or appends it to the bottom of an existing page with the same title, either at the root of a space or inside a specific folder. Works with scoped API tokens that have classic Confluence scopes."
    args_schema: Type[BaseModel] = ConfluenceScopedPageCreatorSchema

    def _run(self, title: str, content: str, space_key: str) -> str:
        api = base_url.rstrip("/")
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        auth = (user_email, api_key)

        try:
            content = md_to_storage(content)
            space_key, folder_id = _resolve_target(api, headers, auth, space_key)
            folder_line = f"folder_id: {folder_id}\n" if folder_id else ""

            search = requests.get(
                f"{api}/rest/api/content",
                headers=headers,
                auth=auth,
                params={"spaceKey": space_key, "title": title, "expand": "body.storage,version"},
                timeout=_TIMEOUT,
            )
            search.raise_for_status()
            results = search.json().get("results", [])

            if results:
                page = results[0]
                page_id = page["id"]
                existing_body = page.get("body", {}).get("storage", {}).get("value", "")
                current_version = page.get("version", {}).get("number", 1)


                update = requests.put(
                    f"{api}/rest/api/content/{page_id}",
                    headers=headers,
                    auth=auth,
                    json={
                        "type": "page",
                        "title": title,
                        "space": {"key": space_key},
                        "version": {"number": current_version + 1},
                        "body": {"storage": {"value": existing_body + "<p></p>" + content, "representation": "storage"}},
                    },
                    timeout=_TIMEOUT,
                )
                update.raise_for_status()
                data = update.json()
                full_link = _page_link(data, api, data.get("_links", {}).get("webui", ""))
                return (
                    f"Content appended to existing page.\n"
                    f"confluence_page_id: {page_id}\nspace_key: {space_key}\n"
                    f"{folder_line}"
                    f"\nPage Title: {title}\nVersion: {current_version + 1}\n"
                )

            create = requests.post(
                f"{api}/rest/api/content",
                headers=headers,
                auth=auth,
                json={
                    "type": "page",
                    "title": title,
                    "space": {"key": space_key},
                    "body": {"storage": {"value": content, "representation": "storage"}},
                },
                timeout=_TIMEOUT,
            )
            create.raise_for_status()
            data = create.json()
            new_id = data.get("id", "")
            full_link = _page_link(data, api, data.get("_links", {}).get("webui", ""))

            move_note = ""
            if folder_id:
                try:
                    move = requests.put(
                        f"{api}/rest/api/content/{new_id}/move/append/{folder_id}",
                        headers=headers, auth=auth, timeout=_TIMEOUT,
                    )
                    move.raise_for_status()
                except requests.RequestException as move_error:
                    resp = getattr(move_error, "response", None)
                    status = resp.status_code if resp is not None else None
                    move_note = (
                        f"\nWARNING: the page was created at the root of space {space_key} but could not be "
                        f"moved into folder {folder_id}: {move_error}{_explain(status)}"
                    )

            return (
                f"Page created successfully.\n"
                f"confluence_page_id: {new_id} \n space_key: {space_key}\n"
                f"{folder_line}"
                f"\nPage Title: {title}\nVersion: 1 "
            )

        except requests.RequestException as e:
            resp = getattr(e, "response", None)
            body = resp.text if resp is not None else ""
            status = resp.status_code if resp is not None else None
            return f"Error writing to Confluence page: {str(e)}\nDetails: {body}{_explain(status)}"
        except Exception as e:
            return f"Error in Confluence Page Creator: {type(e).__name__}: {e}"