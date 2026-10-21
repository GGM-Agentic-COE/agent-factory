# tool-L1-azure-blob-writer

## What does it do?

Creates a virtual folder and uploads a file with specified text content to Azure Blob Storage. In Azure Blob Storage, folders are virtual and represented by blob name prefixes; the tool creates an empty placeholder blob (`folder_name/`) to simulate the folder, then uploads the actual file at `folder_name/file_name`. If the container does not exist, it is created automatically. File names are sanitised to prevent directory traversal attacks. Content is validated and capped at 10 MB before upload.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `connection_string` | **AWS Secrets Manager** — secret `aava-secret-manager-azure-blob-credentials`, key `connection_string` | Azure Storage account connection string. Never appears in the code. Shared with `tool-L1-azure-blob-reader`. |
| `container_name` | Set directly in code | Fixed per deployment — see "SETUP-REQUIRED" comment at the top of the tool file. |
| `blob_storage_url` | Set directly in code | Informational only (used in the returned status message); not a credential. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-azure-blob-writer-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-azure-blob-writer-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-azure-blob-credentials"
secrets = reader._run()
connection_string = secrets.get("connection_string")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no AWS access key or secret is stored in this file; access is granted via the runtime's pod identity.

> `tool-L1-azure-blob-writer.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the connection string as a placeholder value in code.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_name | string | ✓ | Name of the folder to create in Azure Blob Storage (used as blob prefix) |
| file_name | string | ✓ | Name of the file to create inside the folder |
| content | string | ✓ | Text content to write to the file; automatically truncated at 10 MB |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| (return value) | string | Multi-line status string on success, e.g. `"Container 'aava-ggm' already exists. blob_storage_url = '...'\nFolder 'docs' created successfully.\nFile 'report.md' created successfully in folder 'docs'."` |
| (return value) | string | `"Error accessing container. Please try again later or contact support."` on container error |
| (return value) | string | `"Error creating folder. Please try again later or contact support."` on folder creation error |
| (return value) | string | `"Error creating file. Please try again later or contact support."` on file upload error |
| (return value) | string | `"An error occurred while processing your request. Please try again later or contact support."` on unhandled error |

## Standalone tool calling

```python
from tool_L1_azure_blob_writer_secrets_manager import AzureBlobWriterTool

tool = AzureBlobWriterTool()
result = tool._run(
    folder_name="sprint-42/outputs",
    file_name="summary.md",
    content="# Sprint 42 Summary\n\nAll stories completed."
)
```

## Calling tool in agent

Tell the agent the folder to write into, the file name, and the exact content to save. `folder_name` is often an internal identifier (e.g. the current workflow's execution ID) rather than something the end user types; `file_name` and `content` typically come from what the agent itself produced earlier in the workflow:

```
folder_name = <<workflow-execution-id>>
file_name = desired-markdown.md
content = the full markdown file that was produced, VERBATIM
```

If the folder is instead something the end user is naming directly, use:

```
folder_name = {{folder_name}}
```

## Input Sanitisation

`file_name` is sanitised before use:

| Dangerous pattern | Replacement |
|-------------------|-------------|
| `\`, `/`, `*`, `?`, `"`, `<`, `>`, `\|` | `_` |
| `..` (path traversal) | `_` |
| Leading `.`, `/`, `\` | Stripped |
| Empty result after sanitisation | `"default"` |

`folder_name` is **not** sanitised — it is passed through as-is to support nested prefixes (e.g. `project/subfolder`).

`content` is capped at 10 MB (UTF-8 encoded); if it exceeds this limit the content is truncated silently (a warning is logged).

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Timeout | SDK network timeout | Returns error string; details logged |
| Container access denied | Invalid credentials or insufficient permissions | Returns `"Error accessing container..."` |
| Folder creation failure | SDK blob upload error | Returns `"Error creating folder..."` |
| File upload failure | SDK blob upload error | Returns `"Error creating file..."` |
| Content too large | Content > 10 MB | Truncated to 10 MB before upload; warning logged |
| Unhandled exception | Unexpected SDK error | Returns `"An error occurred while processing your request..."` |

## Security Notes

- `connection_string` is retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- `container_name` and `blob_storage_url` are fixed per deployment in code (see Secrets & Configuration above).
- All operations are logged to `azure_blob_operations.log`. Credentials are **never** written to logs.
- `overwrite=True` is passed to all blob uploads — existing files with the same path are silently overwritten.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s default (Azure SDK default) |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Idempotency | `overwrite=True` — safe to re-run with the same inputs |
