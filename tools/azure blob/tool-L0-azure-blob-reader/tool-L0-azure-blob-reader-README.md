# tool-L0-azure-blob-reader

## 1. Executive summary

You give the tool a folder name (a blob prefix). It lists every blob under that prefix in the configured Azure Blob Storage container and downloads each one. It returns all of the files' contents in one formatted text block, with the blob name shown above each file.

**Key points** (details in [Section 6](#6-nuances)):

- The container is fixed in code. You pass only the folder name, not a container name or a blob URL ([6.1](#61-folder-name-is-a-prefix-in-a-fixed-container)).
- Sub-folders are included, and an empty folder name reads the whole container ([6.2](#62-the-read-is-recursive)).
- There is no size limit. Every blob is downloaded in full, and binary files are replaced by a marker ([6.3](#63-no-size-limit-and-binary-files-are-not-returned)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`folder_name`**
```
project-alpha/docs
```

### 2.2 Calling the tool in an agent

`folder_name` changes on every call. The container is fixed in code and the connection string comes from AWS Secrets Manager, so the agent passes neither.

```
folder_name = {{folder_name}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | str | ✓ | Folder (blob prefix) in the configured container whose files should be read, e.g. `project-alpha/docs`. Trailing `/` are stripped and a single `/` is added. Leading `/` is not stripped. An empty value reads the whole container. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| `azure_connection_string` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `azure_connection_string` | Azure Storage account connection string. Read once, when the module is imported, using the pod's IAM role (Pod Identity). The role needs `secretsmanager:GetSecretValue` on the secret. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the name of your secret. |
| `region_name` | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the region the secret lives in. |
| `container_name` | Code — module level | `SETUP-REQUIRED:` placeholder `<your-azure-container-name>`. Replace it with the container to read from. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-azure-blob-reader.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `azure.storage.blob` | `azure-storage-blob` | `BlobServiceClient` to list and download blobs (`BlobClient` and `ContainerClient` are imported but not used directly) |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `logging` | stdlib | Writes operations and errors to `azure_blob_operations.log` |
| `re` | stdlib | Imported, not used |
| `os` | stdlib | Imported, not used |
| `json` | stdlib | Parses the secret string |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` when reading the secret |
| `typing` | stdlib | Type hints |

---

## 6. Nuances

### 6.1 Folder name is a prefix in a fixed container
The tool always reads from `container_name`. `folder_name` is used as a blob prefix, so a container name, `https://` URL or leading `/` in the value matches nothing and returns `No files found in folder '<folder_name>'.` **Do:** pass only the path inside the container, e.g. `project-alpha/docs`, with no leading slash.

### 6.2 The read is recursive
Every blob whose name starts with `<folder_name>/` is returned, including blobs in sub-folders, in the order Azure lists them. Blobs whose names end in `/` (folder markers) are skipped. If `folder_name` is empty, the prefix is empty and every blob in the container is read. **Do:** always pass a folder name, and point the tool at the narrowest folder you need so large trees are not pulled into the agent's context.

### 6.3 No size limit, and binary files are not returned
Each blob is downloaded in full with no size cap. Blobs that are not valid UTF-8 (PDF, images, archives) are still downloaded, but their content shows `[Binary content, <n> bytes — not displayed as text]`. **Do:** use this tool for folders of text files only, and check for the marker before passing the content on.

### 6.4 A failed file does not stop the read
If one blob fails to download, its section shows `[Error reading this file]` and the other files are still returned. The `Read <n> file(s)` count excludes failed files. If every file fails, the tool returns `Folder '<folder_name>' contains no readable files (only the folder marker).` even though the files exist. **Do:** search the output for `[Error reading this file]` when completeness matters, and check `azure_blob_operations.log` if the "no readable files" message is unexpected.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at module import) | Read `azure_connection_string` from the secret named in `SECRET_NAME` |
| 2 | `ContainerClient.exists()` (`GET` container properties) | Confirm the container exists |
| 3 | `ContainerClient.list_blobs(name_starts_with=<prefix>)` (List Blobs, paginated by the SDK) | List every blob under the prefix |
| 4 | `BlobClient.download_blob().readall()` (Get Blob, per blob) | Download each file's content |

### 7.2 Returns

**Success**
```
Read <n> file(s) from folder '<folder_name>':

===== FILE: <blob name> =====
<file content | [Binary content, <n> bytes — not displayed as text] | [Error reading this file]>

===== FILE: <blob name> =====
...
```

**Error**
```
<message>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Container '<container_name>' does not exist.` | The configured container is not in the storage account | Check `container_name` and the storage account in the connection string |
| `No files found in folder '<folder_name>'.` | No blob starts with the prefix | Check the folder name, its case, and that it has no leading `/` |
| `Folder '<folder_name>' contains no readable files (only the folder marker).` | Only folder-marker blobs exist under the prefix, or every download failed | Check the folder has files; check the log for download errors |
| `An error occurred while reading the folder` | Any other failure, e.g. missing or invalid connection string, authentication or network error | Check `azure_blob_operations.log` for the logged exception |
| `RuntimeError: Error retrieving secret: <detail>` / `RuntimeError: Unexpected error: <detail>` | Raised at import when the secret cannot be read or is not a JSON object | Check `SECRET_NAME`, `region_name`, the Pod Identity association and `secretsmanager:GetSecretValue` on the role |

### 7.3 Known limitations

- Read-only. It cannot write, overwrite or delete blobs.
- Reads one container, set in code. There is no parameter to choose the container or storage account.
- No filter by file type, date or name pattern. Everything under the prefix is returned.
- No option to stop recursion into sub-folders or to limit file size or count.
- Text only. Binary formats are not parsed or extracted.
- Output does not include blob size or last-modified time.

### 7.4 Security & resilience

**Security**
- No credentials are stored in code. The connection string is read from AWS Secrets Manager using the pod's IAM role and is never logged.
- Exceptions are logged with stack traces to `azure_blob_operations.log` in the working directory; the caller only receives a generic message.
- File contents are also printed to stdout, so they can appear in container logs.
- The connection string usually grants account-wide access. Use a SAS-based connection string scoped to read and list on the container where possible.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | No explicit timeout; Azure SDK defaults apply | Pass `connection_timeout` and `read_timeout` to `BlobServiceClient.from_connection_string` |
| Retry | Azure SDK default retry policy only; no tool-level retry. The secret is read once at import with no retry | Configure an explicit `retry_total` on the client; handle secret-read failure without failing import |
| Concurrency | Blobs are downloaded one at a time | Use a bounded thread pool for large folders |
| Input validation | `folder_name` only has trailing `/` normalised; an empty value reads the whole container; no size cap on downloads | Reject empty folder names and add a per-file size limit |
