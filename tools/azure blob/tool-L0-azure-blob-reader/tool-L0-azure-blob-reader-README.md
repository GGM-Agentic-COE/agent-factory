# tool-L1-azure-blob-reader

## What does it do?

Reads and returns the decoded text contents of every file inside a specified folder (virtual prefix) in Azure Blob Storage. The tool lists all blobs under the given folder prefix, downloads each one, and returns a formatted string that includes the file name and its content. Binary or non-UTF-8 files are noted with their byte size instead of content. The folder marker blob itself (the empty `folder_name/` placeholder) is skipped automatically.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `connection_string` | **AWS Secrets Manager** — secret `aava-secret-manager-azure-blob-credentials`, key `connection_string` | Azure Storage account connection string. Never appears in the code. |
| `container_name` | Set directly in code | Fixed per deployment — see "SETUP-REQUIRED" comment at the top of the tool file. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-azure-blob-reader-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-azure-blob-reader-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-azure-blob-credentials"
secrets = reader._run()
connection_string = secrets.get("connection_string")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no AWS access key or secret is stored in this file; access is granted via the runtime's pod identity.

> `tool-L1-azure-blob-reader.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the connection string as a placeholder value in code.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_name | string | ✓ | Name of the folder (blob prefix) in Azure Blob Storage to read all files from |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| (return value) | string | `"Read N file(s) from folder '<name>':\n\n===== FILE: <path> =====\n<content>\n..."` on success |
| (return value) | string | `"No files found in folder '<name>'."` when the folder is empty |
| (return value) | string | `"Container '<name>' does not exist."` when the container is missing |
| (return value) | string | `"An error occurred while reading the folder"` on unhandled SDK/network error |

Each `===== FILE: <blob-path> =====` section contains either the decoded UTF-8 text or a note: `[Binary content, N bytes — not displayed as text]`.

## Standalone tool calling

Call the tool directly from Python (e.g. from a CrewAI orchestrator script, outside of an agent):

```python
from tool_L1_azure_blob_reader_secrets_manager import AzureBlobReaderTool

tool = AzureBlobReaderTool()
result = tool._run(folder_name="my-project/docs")
```

## Calling tool in agent

Tell the agent which folder to read. `folder_name` is the only input:

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
| Container not found | The configured container does not exist | Returns `"Container '<name>' does not exist."` |
| No files in folder | Prefix matches no blobs (or only the folder marker) | Returns `"No files found in folder '<name>'."` or `"Folder '<name>' contains no readable files"` |
| Individual blob download failure | Transient SDK error on a single blob | Logs error at ERROR level; marks file section with `[Error reading this file]` and continues |
| Binary / non-UTF-8 content | File cannot be decoded as UTF-8 | Marks section with `[Binary content, N bytes — not displayed as text]` |
| Unhandled exception | SDK initialisation failure or network error | Logs full traceback; returns `"An error occurred while reading the folder"` |

## Security Notes

- `connection_string` is retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- `container_name` is fixed per deployment in code (see Secrets & Configuration above).
- All operations are logged to `azure_blob_operations.log`. Credentials are **never** written to logs.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s default (Azure SDK default) |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Partial failure | Per-blob errors are isolated; other files in the folder continue to be read |
