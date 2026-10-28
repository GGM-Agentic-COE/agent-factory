# tool-L0-azure-blob-files-reader

## 1. Summary

You give the tool a folder name (a blob prefix) and a list of file names inside it. It downloads only those files from the configured Azure Blob Storage container and returns their contents in one formatted text block, with the blob path shown above each file and a footer listing any files that were missing or failed.

**Key points** (details in [Section 6](#6-nuances)):

- `file_names` accepts a list, a JSON array string or a comma-separated string ([6.1](#61-file_names-accepts-several-formats)).
- A file name that already starts with the folder prefix is not prefixed again ([6.2](#62-how-each-file-path-is-built)).
- A missing or unreadable file does not stop the read; it is marked in place and listed in a footer ([6.3](#63-missing-and-failed-files-are-reported-not-fatal)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`folder_name`**
```
project-alpha/docs
```

**`file_names`**
```
["summary.md", "findings.md"]
```

### 2.2 Calling the tool in an agent

Both parameters change per call. `folder_name` is often a workflow identifier from an earlier step, and `file_names` lists the files that step produced. The container is fixed in code.

```
folder_name = {{folder_name}}
file_names = {{file_names}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | str | ✓ | Folder (blob prefix) in the configured container that holds the files, e.g. `project-alpha/docs`. Trailing `/` are stripped and a single `/` is added. An empty value means the container root. |
| `file_names` | List[str] | ✓ | File names inside the folder to read, e.g. `["summary.md", "findings.md"]`. Also accepts a JSON array string or a comma-separated string (`summary.md, findings.md`). Surrounding quotes and spaces are removed, empty entries are dropped, a leading `/` is stripped, and duplicates are read once. Names may include a sub-path (`sub/notes.md`) or the full folder path. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| `azure_connection_string` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `azure_connection_string` | Azure Storage account connection string. Read once, when the module is imported, using the pod's IAM role (Pod Identity). The role needs `secretsmanager:GetSecretValue` on the secret. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the name of your secret. |
| `region_name` | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the region the secret lives in. |
| `container_name` | Code — module level | `SETUP-REQUIRED:` placeholder `<your-azure-container-name>`. Replace it with the container to read from. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-azure-blob-files-reader.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `json` | stdlib | Parses the secret string and JSON-string `file_names` |
| `boto3` | `boto3` | Secrets Manager client |
| `logging` | stdlib | Writes operations and errors to `azure_blob_operations.log` |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`, `field_validator`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `azure.storage.blob` | `azure-storage-blob` | `BlobServiceClient` to check and download blobs (`BlobClient` and `ContainerClient` are imported but not used directly) |
| `botocore.exceptions` | `botocore` | `ClientError` when reading the secret |

---

## 6. Nuances

### 6.1 `file_names` accepts several formats
A real list is used as-is. A string is first parsed as JSON (`["a.md","b.md"]`); if that fails it is split on commas (`a.md, b.md`). A single value becomes a one-item list. Each entry is trimmed of spaces and quotes, and empty entries are removed. If nothing is left, the tool returns `No file names were provided. Provide at least one file name to read.` **Do:** pass a JSON list of names; avoid commas inside file names, because comma-separated input will split them.

### 6.2 How each file path is built
Each name has a leading `/` removed. If it already starts with `<folder_name>/`, it is used as the full blob path; otherwise `<folder_name>/` is put in front. So `summary.md` and `project-alpha/docs/summary.md` both read the same blob, and that blob is read once. Only exact names are matched: there are no wildcards and no case-insensitive matching. **Do:** pass names exactly as stored, either relative to the folder or as the full path.

### 6.3 Missing and failed files are reported, not fatal
A file that does not exist shows `[File not found in folder]`; a file whose check or download fails shows `[Error reading this file]`. The other files are still returned, and a footer lists `Files not found:` and `Files that failed to download:`. Only if no requested file can be read does the tool return `None of the requested files were readable in folder '<folder_name>'. Requested: <names>.` **Do:** compare `Read <n> of <m>` in the header, and check the footer before relying on the output.

### 6.4 No size limit, and binary files are not returned
Each requested file is downloaded in full with no size cap. Files that are not valid UTF-8 (PDF, images, archives) show `[Binary content, <n> bytes — not displayed as text]` and still count as read. **Do:** request text files only, and check for the marker before passing the content on.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at module import) | Read `azure_connection_string` from the secret named in `SECRET_NAME` |
| 2 | `ContainerClient.exists()` (`GET` container properties) | Confirm the container exists |
| 3 | `BlobClient.exists()` (`HEAD` blob, per requested file) | Check whether the file exists |
| 4 | `BlobClient.download_blob().readall()` (Get Blob, per existing file) | Download the file's content |

### 7.2 Returns

**Success**
```
Read <n> of <m> requested file(s) from folder '<folder_name>':

===== FILE: <blob path> =====
<file content | [Binary content, <n> bytes — not displayed as text] | [File not found in folder] | [Error reading this file]>

===== FILE: <blob path> =====
...

Files not found: <blob path>, <blob path>
Files that failed to download: <blob path>
```
The footer lines appear only when there are missing or failed files. Files appear in the order requested.

**Error**
```
<message>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `No file names were provided. Provide at least one file name to read.` | `file_names` was empty after clean-up | Pass at least one file name |
| `Container '<container_name>' does not exist.` | The configured container is not in the storage account | Check `container_name` and the storage account in the connection string |
| `None of the requested files were readable in folder '<folder_name>'. Requested: <names>.` | Every requested file was missing or failed to download | Check the folder and file names, their case, and the log |
| `An error occurred while reading the folder` | Any other failure, e.g. invalid input, missing or invalid connection string, authentication or network error | Check `azure_blob_operations.log` for the logged exception |
| `RuntimeError: Error retrieving secret: <detail>` / `RuntimeError: Unexpected error: <detail>` | Raised at import when the secret cannot be read or is not a JSON object | Check `SECRET_NAME`, `region_name`, the Pod Identity association and `secretsmanager:GetSecretValue` on the role |

### 7.3 Known limitations

- Read-only. It cannot write, overwrite or delete blobs.
- Reads one container, set in code. There is no parameter to choose the container or storage account.
- Reads only the named files. It cannot list a folder or match wildcards; use `tool-L0-azure-blob-reader` to read a whole folder.
- Text only. Binary formats are not parsed or extracted.
- Output does not include blob size or last-modified time.

### 7.4 Security & resilience

**Security**
- No credentials are stored in code. The connection string is read from AWS Secrets Manager using the pod's IAM role and is never logged.
- Exceptions are logged with stack traces to `azure_blob_operations.log` in the working directory; the caller only receives a generic message.
- File contents are also printed to stdout, so they can appear in container logs.
- Only the named blobs are accessed; the folder is never listed.
- The connection string usually grants account-wide access. Use a SAS-based connection string scoped to read on the container where possible.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | No explicit timeout; Azure SDK defaults apply | Pass `connection_timeout` and `read_timeout` to `BlobServiceClient.from_connection_string` |
| Retry | Azure SDK default retry policy only; no tool-level retry. The secret is read once at import with no retry | Configure an explicit `retry_total` on the client; handle secret-read failure without failing import |
| Concurrency | Files are checked and downloaded one at a time (two calls per file) | Use a bounded thread pool, and drop the separate `exists()` call by catching `ResourceNotFoundError` on download |
| Input validation | `file_names` coerced and de-duplicated; `folder_name` only has trailing `/` normalised; no size cap on downloads | Reject empty folder names and add a per-file size limit |
