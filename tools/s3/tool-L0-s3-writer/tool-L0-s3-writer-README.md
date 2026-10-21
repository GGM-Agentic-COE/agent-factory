# tool-L1-s3-writer

## What does it do?

Uploads text content to a fixed S3 bucket under a caller-specified folder. The object key is built as `<folder>/<UTC-timestamp>_<file_name>` — the timestamp prefix means repeated uploads with the same `file_name` never collide or overwrite each other. `file_name` is sanitised to its basename only (any path components are stripped) before being used in the key.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `AWS_ACCESS_KEY_ID` | **AWS Secrets Manager** — secret `aava-secret-manager-s3-credentials`, key `aws_access_key_id` | Never appears in the code. Shared with `tool-L1-s3-reader`. |
| `AWS_SECRET_ACCESS_KEY` | **AWS Secrets Manager** — same secret, key `aws_secret_access_key` | Never appears in the code. |
| `BUCKET_NAME` | Set directly in code | Not a secret — the S3 bucket this tool writes to. Must match `tool-L1-s3-reader`'s `BUCKET_NAME`. See "CHANGE THIS" comment at the top of the tool file. |
| `AWS_REGION` | Set directly in code | Not a secret — the bucket's AWS region. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME`/`region_name` on the `AWSSecretReaderPodIdentity` class and `BUCKET_NAME`/`AWS_REGION` on `S3UploadTool` — is tagged `SETUP-REQUIRED:` directly in `tool-L1-s3-writer-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-s3-writer-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-s3-credentials"
secrets = reader._run()

class S3UploadTool(BaseTool):
    AWS_ACCESS_KEY_ID: str = secrets.get("aws_access_key_id")
    AWS_SECRET_ACCESS_KEY: str = secrets.get("aws_secret_access_key")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file.

> **Note on this tool's history:** unlike the other tools in this repository, `tool-L1-s3-writer.py` (without the `-secrets-manager` suffix) never had real AWS keys hardcoded — it shipped with literal placeholder text (`"ENTER ACCESS KEY HERE"` / `"ENTER SECRET HERE"`) that must be filled in before that debug copy will work. It is kept in this folder only for local debugging and is not used in production.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_name | string | ✓ | Name of the folder (prefix) in the S3 bucket to upload into, e.g. `"incoming"` |
| file_name | string | ✓ | Name of the file to create, e.g. `"report.txt"`. Any path components are stripped — only the basename is used. |
| contents | string | ✓ | Text content to write into the file |

## Returns

On success:

```json
{
  "status": "SUCCESS",
  "bucket": "<bucket-name>",
  "key": "<folder>/<YYYYMMDD_HHMMSS>_<file_name>",
  "folder": "<folder>/",
  "size_bytes": 1234,
  "uploaded_at": "<YYYYMMDD_HHMMSS>"
}
```

On failure:

```json
{"status": "FAILED", "reason": "<S3_CLIENT_INIT_FAILED | INVALID_FILE_NAME | S3_UPLOAD_FAILED>: <detail>"}
```

## Standalone tool calling

```python
from tool_L1_s3_writer_secrets_manager import S3UploadTool

tool = S3UploadTool()
result = tool._run(
    folder_name="incoming/reports",
    file_name="summary.md",
    contents="# Sprint 42 Summary\n\nAll stories completed."
)
print(result["key"])  # "incoming/reports/20260804_153000_summary.md"
```

## Calling tool in agent

`folder_name` is often an internal identifier (e.g. the current workflow's execution ID) rather than something the end user types; `file_name` and `contents` typically come from what the agent itself produced earlier in the workflow:

```
folder_name = <<workflow-execution-id>>
file_name = desired-report.md
contents = the full report content that was produced, VERBATIM
```

If the folder is instead something the end user is naming directly, use:

```
folder_name = {{folder_name}}
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Invalid credentials | Bad AWS access key/secret | Returns `{"status": "FAILED", "reason": "S3_CLIENT_INIT_FAILED: ..."}` |
| Empty file name after stripping | `file_name` was empty, `/`, or otherwise resolved to nothing | Returns `{"status": "FAILED", "reason": "INVALID_FILE_NAME"}` |
| Upload failure | Bucket doesn't exist, access denied, or other `put_object` error | Returns `{"status": "FAILED", "reason": "S3_UPLOAD_FAILED: ..."}` |

## Security Notes

- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- `BUCKET_NAME` and `AWS_REGION` are fixed per deployment in code (see Secrets & Configuration above) and must match the reader tool's values.
- `file_name` is reduced to its basename (`.strip("/").split("/")[-1]`) before use — this prevents a caller from writing outside the intended folder via a path-traversal-style file name, but does not otherwise validate or sanitise the name.
- Error messages returned to the caller include the raw exception text (`{e}`), which may surface boto3/AWS error details — review before exposing this tool's output to end users if that detail is sensitive in your environment.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Collision avoidance | Every object key is prefixed with a UTC timestamp (`YYYYMMDD_HHMMSS`), so repeated uploads of the same `file_name` never overwrite each other |
| Idempotency | Not idempotent by design — each call creates a new, uniquely-named object rather than overwriting an existing one |
| Path safety | `file_name` is reduced to its basename before being combined with `folder_name` |
