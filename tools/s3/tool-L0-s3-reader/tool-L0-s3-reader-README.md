# tool-L1-s3-reader

## What does it do?

Reads and returns the contents of every file inside a given folder (prefix) of a fixed S3 bucket. Files are listed via the paginated `list_objects_v2` API, sorted by key, and each one is downloaded and decoded as UTF-8 text. Files larger than 1 MB are skipped rather than downloaded; binary or non-UTF-8 content is flagged instead of causing a failure. The zero-byte "folder marker" object that S3 consoles sometimes create is skipped automatically.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `AWS_ACCESS_KEY_ID` | **AWS Secrets Manager** — secret `aava-secret-manager-s3-credentials`, key `aws_access_key_id` | Never appears in the code. Shared with `tool-L1-s3-writer`. |
| `AWS_SECRET_ACCESS_KEY` | **AWS Secrets Manager** — same secret, key `aws_secret_access_key` | Never appears in the code. |
| `BUCKET_NAME` | Set directly in code | Not a secret — the S3 bucket this tool reads from. See "CHANGE THIS" comment at the top of the tool file. |
| `AWS_REGION` | Set directly in code | Not a secret — the bucket's AWS region. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME`/`region_name` on the `AWSSecretReaderPodIdentity` class and `BUCKET_NAME`/`AWS_REGION` on `S3DocumentRetriever` — is tagged `SETUP-REQUIRED:` directly in `tool-L1-s3-reader-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-s3-reader-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-s3-credentials"
secrets = reader._run()

class S3DocumentRetriever(BaseTool):
    AWS_ACCESS_KEY_ID: str = secrets.get("aws_access_key_id")
    AWS_SECRET_ACCESS_KEY: str = secrets.get("aws_secret_access_key")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file.

> **Note on this tool's history:** unlike the other tools in this repository, `tool-L1-s3-reader.py` (without the `-secrets-manager` suffix) never had real AWS keys hardcoded — it shipped with literal placeholder text (`"ENTER ACCESS KEY HERE"` / `"ENTER SECRET HERE"`) that must be filled in before that debug copy will work. It is kept in this folder only for local debugging and is not used in production.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_name | string | ✓ | Name of the folder (prefix) in the S3 bucket whose files should be read |

## Returns

A single formatted string:

```
FILE_SOURCE: S3
BUCKET: <bucket-name>
FOLDER: <prefix>/
FILE_COUNT: N

===== FILE: <key> =====
LAST_MODIFIED: <timestamp>
SIZE_BYTES: <size>

<file content, or a skip/error marker>
...
```

| Return value | Cause |
|---------------|-------|
| `"S3_CLIENT_INIT_FAILED: <error>"` | boto3 client construction failed (e.g. malformed credentials) |
| `"S3_LIST_FAILED: <error>"` | `list_objects_v2` call failed (e.g. bucket doesn't exist, access denied) |
| `"S3_RETRIEVE_FAILED: No files found under folder '<prefix>'"` | Folder exists but is empty (or only contains the zero-byte marker) |
| `[SKIPPED: file exceeds size limit]` | Per-file, when the object is larger than `MAX_FILE_BYTES` (1 MB) |
| `[READ_FAILED: <error>]` | Per-file, when downloading that specific object fails |
| `[BINARY OR NON-UTF8 CONTENT: N bytes]` | Per-file, when the object can't be decoded as UTF-8 text |

## Standalone tool calling

```python
from tool_L1_s3_reader_secrets_manager import S3DocumentRetriever

tool = S3DocumentRetriever()
result = tool._run(folder_name="incoming/reports")
```

## Calling tool in agent

`folder_name` is the only input:

```
folder_name = {{folder_name}}
```

For example, if a prior step in the workflow wrote its output to a folder named after the run itself, the agent would instead be told to reuse that identifier rather than ask the user for one:

```
folder_name = <<workflow-execution-id>>
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Invalid credentials | Bad AWS access key/secret | Returns `"S3_CLIENT_INIT_FAILED: ..."` |
| Bucket doesn't exist / access denied | Wrong `BUCKET_NAME` or insufficient IAM permissions | Returns `"S3_LIST_FAILED: ..."` |
| Empty folder | No objects under the given prefix | Returns `"S3_RETRIEVE_FAILED: No files found under folder '...'"` |
| Oversized file | Object larger than 1 MB | That file's body is replaced with `[SKIPPED: file exceeds size limit]`; other files still returned |
| Per-file read failure | Transient S3 error on a single object | That file's body is replaced with `[READ_FAILED: ...]`; other files still returned |
| Binary content | Object isn't valid UTF-8 | That file's body is replaced with `[BINARY OR NON-UTF8 CONTENT: N bytes]` |

## Security Notes

- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- `BUCKET_NAME` and `AWS_REGION` are fixed per deployment in code (see Secrets & Configuration above).
- Error messages returned to the caller include the raw exception text (`{e}`), which may surface boto3/AWS error details — review before exposing this tool's output to end users if that detail is sensitive in your environment.

## Resilience

| Concern | Configuration |
|---------|--------------|
| File size limit | Files over 1 MB (`MAX_FILE_BYTES`) are skipped rather than downloaded |
| Partial failure | Per-object list/read errors are isolated; other files in the folder continue to be returned |
| Pagination | `list_objects_v2` is paginated automatically via `get_paginator`, so folders with many objects are fully enumerated |
| Folder markers | The zero-byte "folder" placeholder object is skipped automatically |
