# tool-L0-azure-blob-writer

## 1. Executive summary

You give the tool a folder name, a file name and the text content. It writes the content as a blob at `<folder_name>/<file_name>` in the configured Azure Blob Storage container, creating the container and a folder-marker blob if needed. It returns a short status message, one line per step.

**Key points** (details in [Section 6](#6-nuances)):

- Existing files are overwritten without warning ([6.1](#61-existing-files-are-overwritten)).
- `file_name` is sanitised (slashes and special characters become `_`), but `folder_name` is used exactly as given ([6.2](#62-file-name-is-sanitised-folder-name-is-not)).
- Content over 10 MB is cut off silently ([6.3](#63-content-over-10-mb-is-truncated)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`folder_name`**
```
project-alpha/outputs
```

**`file_name`**
```
summary.md
```

**`content`**
```
# Sprint summary

All stories completed. Two defects carried over.
```

### 2.2 Calling the tool in an agent

All three parameters change per call. `folder_name` is often a workflow identifier rather than something the user types. `file_name` and `content` usually come from what the agent produced earlier in the workflow. The container is fixed in code.

```
folder_name = {{folder_name}}
file_name = {{file_name}}
content = the full file content produced earlier, verbatim
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | str | ✓ | Folder (blob prefix) to write into, e.g. `project-alpha/outputs`. Used as-is; nested paths with `/` are allowed. |
| `file_name` | str | ✓ | Name of the file to create, including the extension, e.g. `summary.md`. The characters `\ / * ? : " < > \|` and `..` are replaced with `_`, leading `.`, `/` and `\` are stripped, and an empty result becomes `default`. |
| `content` | str | ✓ | Text to write: plain text, JSON, CSV, Markdown or any string. Maximum 10 MB; longer content is truncated. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| `azure_connection_string` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `azure_connection_string` | Azure Storage account connection string. Read once, when the module is imported, using the pod's IAM role (Pod Identity). The role needs `secretsmanager:GetSecretValue` on the secret. The connection string must allow writing blobs, and creating the container if it may not exist. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the name of your secret. |
| `region_name` | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the region the secret lives in. |
| `container_name` | Code — module level | `SETUP-REQUIRED:` placeholder `<your-azure-container-name>`. Replace it with the container to write to. |
| `blob_storage_url` | Code — module level | `SETUP-REQUIRED:` placeholder `<your-storage-account>.blob.core.windows.net/<your-azure-container-name>`. Shown in the success message only; it does not control where the file is written. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-azure-blob-writer.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `azure.storage.blob` | `azure-storage-blob` | `BlobServiceClient` to create the container and upload blobs (`BlobClient` and `ContainerClient` are imported but not used directly) |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `logging` | stdlib | Writes operations, sanitisation warnings and errors to `azure_blob_operations.log` |
| `re` | stdlib | Sanitises `file_name` |
| `os` | stdlib | Imported, not used |
| `json` | stdlib | Parses the secret string |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` when reading the secret |
| `typing` | stdlib | Type hints |

---

## 6. Nuances

### 6.1 Existing files are overwritten
Both the folder-marker blob (`<folder_name>/`) and the file blob are uploaded with `overwrite=True`. A file with the same path is replaced with no warning, and the message still says `created successfully`. **Do:** use a unique file name (e.g. include a run ID or timestamp) when earlier versions must be kept.

### 6.2 File name is sanitised, folder name is not
`file_name` has `\ / * ? : " < > |` and `..` replaced with `_` and leading `.`, `/`, `\` removed, so `reports/q1.md` becomes `reports_q1.md` and `.env` becomes `env`. The sanitised name is what is written and reported. `folder_name` is not changed at all, so nested paths work, but so do leading slashes, `..` and an empty value (which writes to `/` and `/<file_name>`). **Do:** put any sub-path in `folder_name`, not `file_name`; pass a clean, non-empty folder name with no leading `/`; and read the returned file name rather than assuming the one you sent.

### 6.3 Content over 10 MB is truncated
If the UTF-8 size of `content` exceeds 10 MB (10,485,760 bytes), the content is cut to the first 10,485,760 characters and uploaded. The caller is not told; a warning goes only to the log. Because the cut is by characters, content with multi-byte characters can still be larger than 10 MB after truncation. **Do:** keep content well under 10 MB, or split large output across several files.

### 6.4 The container is created if missing
If `container_name` does not exist, the tool creates it and the first line of the result reads `Container '<container_name>' created successfully.` This needs a connection string with permission to create containers. **Do:** check the first result line; an unexpected "created" usually means `container_name` or the storage account is wrong.

### 6.5 The upload content type is not set
The blob is uploaded as a plain string with no content type or other settings, regardless of the file extension. **Do:** if downstream tools rely on the blob's content type (e.g. for browser display), set it outside this tool.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at module import) | Read `azure_connection_string` from the secret named in `SECRET_NAME` |
| 2 | `ContainerClient.exists()` (`GET` container properties) | Check whether the container exists |
| 3 | `BlobServiceClient.create_container()` (Create Container, only if missing) | Create the container |
| 4 | `BlobClient.upload_blob("", overwrite=True)` (Put Blob on `<folder_name>/`) | Create the empty folder-marker blob |
| 5 | `BlobClient.upload_blob(content, overwrite=True)` (Put Blob on `<folder_name>/<file_name>`) | Write the file |

### 7.2 Returns

**Success**
```
Container '<container_name>' already exists. blob_storage_url = '<blob_storage_url>'
Folder '<folder_name>' created successfully.
File '<sanitised file_name>' created successfully in folder '<folder_name>'.
```
The first line reads `Container '<container_name>' created successfully. blob_storage_url = '<blob_storage_url>'` when the container was created.

**Error**
```
<message>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Error accessing container. Please try again later or contact support.` | Checking or creating the container failed: authentication, permissions, network, or invalid container name | Check the connection string, `container_name` and `azure_blob_operations.log` |
| `Error creating folder. Please try again later or contact support.` | Uploading the folder-marker blob failed | Check write permission and `folder_name`; see the log |
| `Error creating file. Please try again later or contact support.` | Uploading the file blob failed | Check write permission, content size and `file_name`; see the log |
| `An error occurred while processing your request. Please try again later or contact support.` | Any other failure, e.g. missing or invalid connection string | Check the secret has `azure_connection_string`; see the log |
| `RuntimeError: Error retrieving secret: <detail>` / `RuntimeError: Unexpected error: <detail>` | Raised at import when the secret cannot be read or is not a JSON object | Check `SECRET_NAME`, `region_name`, the Pod Identity association and `secretsmanager:GetSecretValue` on the role |

### 7.3 Known limitations

- Writes one file per call. No batch upload.
- Cannot append, read or delete. Writes always overwrite.
- Writes to one container, set in code. There is no parameter to choose the container or storage account.
- Text only. There is no way to upload binary content or set a content type or metadata.
- Always creates a folder-marker blob, even if the folder already has files.

### 7.4 Security & resilience

**Security**
- No credentials are stored in code. The connection string is read from AWS Secrets Manager using the pod's IAM role and is never logged.
- Exceptions are logged with stack traces to `azure_blob_operations.log` in the working directory; the caller only receives a generic message.
- `file_name` is sanitised against path traversal; `folder_name` is not.
- The connection string usually grants account-wide access. Use a SAS-based connection string scoped to the container where possible.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | No explicit timeout; Azure SDK defaults apply | Pass `connection_timeout` and `read_timeout` to `BlobServiceClient.from_connection_string` |
| Retry | Azure SDK default retry policy only; no tool-level retry. The secret is read once at import with no retry | Configure an explicit `retry_total` on the client; handle secret-read failure without failing import |
| Concurrency | One upload per call; concurrent calls to the same path overwrite each other (last write wins) | Use unique file names per run, or upload with an `if_none_match="*"` condition where overwrite is not wanted |
| Input validation | `file_name` sanitised; `folder_name` not validated; `content` truncated silently by characters at 10 MB | Validate `folder_name` (non-empty, no leading `/` or `..`) and return an error instead of truncating |
