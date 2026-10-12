# tool-L1-azure-blob-specific-files-reader

## What does it do?

Reads and returns the decoded text contents of **only the named files** inside a specified folder (virtual prefix) in Azure Blob Storage. The tool takes a folder name plus an explicit list of file names, resolves each one to a full blob path under that prefix, downloads it individually, and returns a formatted string that includes the file name and its content. The folder is never listed, so files that were not requested are never touched. Binary or non-UTF-8 files are noted with their byte size instead of content. Requested files that do not exist are reported per-file and summarised at the end of the output rather than aborting the run.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `connection_string` | **AWS Secrets Manager** — secret `aava-secret-manager-azure-blob-credentials`, key `connection_string` | Azure Storage account connection string. Never appears in the code. |
| `container_name` | Set directly in code | Fixed per deployment — see "SETUP-REQUIRED" comment at the top of the tool file. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-azure-blob-specific-files-reader-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-azure-blob-specific-files-reader-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-azure-blob-credentials"
secrets = reader._run()
connection_string = secrets.get("connection_string")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no AWS access key or secret is stored in this file; access is granted via the runtime's pod identity.

> `tool-L1-azure-blob-specific-files-reader.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the connection string as a placeholder value in code.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_name | string | ✓ | Name of the folder (blob prefix) in Azure Blob Storage that contains the files |
| file_names | list[string] | ✓ | The specific file names inside that folder to read, e.g. `["file-1.md", "file-2.md"]`. Only these files are read. Accepts bare names (`file-1.md`) or prefix-qualified paths (`my_folder/file-1.md`); the folder prefix is not doubled. A JSON-string or comma-separated string is coerced to a list. Duplicates are read once. |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| (return value) | string | `"Read N of M requested file(s) from folder '<name>':\n\n===== FILE: <path> =====\n<content>\n..."` on success |
| (return value) | string | `"No file names were provided. Provide at least one file name to read."` when `file_names` is empty |
| (return value) | string | `"None of the requested files were readable in folder '<name>'. Requested: <names>."` when every requested file is missing or failed |
| (return value) | string | `"Container '<name>' does not exist."` when the container is missing |
| (return value) | string | `"An error occurred while reading the folder"` on unhandled SDK/network error |

Each `===== FILE: <blob-path> =====` section contains either the decoded UTF-8 text or a note: `[Binary content, N bytes — not displayed as text]`, `[File not found in folder]`, or `[Error reading this file]`.

On a partial success the returned string ends with a footer listing the unreadable files:

```
Files not found: my_folder/file-3.md
Files that failed to download: my_folder/file-4.md
```

## Standalone tool calling

Call the tool directly from Python (e.g. from a CrewAI orchestrator script, outside of an agent):

```python
from tool_L1_azure_blob_specific_files_reader_secrets_manager import AzureBlobReaderTool

tool = AzureBlobReaderTool()
result = tool._run(folder_name="my-project/docs", file_names=["file-1.md", "file-2.md"])
```

## Calling tool in agent

Tell the agent which folder to read and which files inside it. Both inputs are required:

```
folder_name = {{folder_name}}
file_names = {{file_names}}
```

For example, if a prior step in the workflow wrote its output to a folder named after the run itself and only certain artefacts of that run are needed, the agent would be told to reuse that identifier rather than ask the user for one:

```
folder_name = <<workflow-execution-id>>
file_names = ["summary.md", "findings.md"]
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Container not found | The configured container does not exist | Returns `"Container '<name>' does not exist."` |
| Empty file list | `file_names` resolved to an empty list | Returns `"No file names were provided. Provide at least one file name to read."` |
| Requested file not found | Named file does not exist under the folder prefix | Logs at INFO level; marks file section with `[File not found in folder]`, lists it under "Files not found", and continues |
| No requested file readable | Every named file is missing or failed | Returns `"None of the requested files were readable in folder '<name>'. Requested: <names>."` |
| Individual blob download failure | Transient SDK error on a single blob | Logs error at ERROR level; marks file section with `[Error reading this file]`, lists it under "Files that failed to download", and continues |
| Binary / non-UTF-8 content | File cannot be decoded as UTF-8 | Marks section with `[Binary content, N bytes — not displayed as text]` |
| Unhandled exception | SDK initialisation failure or network error | Logs full traceback; returns `"An error occurred while reading the folder"` |

## Security Notes

- `connection_string` is retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- `container_name` is fixed per deployment in code (see Secrets & Configuration above).
- Requested file names are resolved strictly under the given folder prefix, and only the named blobs are downloaded — the folder is never enumerated.
- All operations are logged to `azure_blob_operations.log`. Credentials are **never** written to logs.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s default (Azure SDK default) |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Partial failure | Per-file errors are isolated; a missing or failed file is reported in place and the remaining requested files continue to be read |