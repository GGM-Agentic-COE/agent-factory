# tool-L0-s3-reader

## 1. Summary

You give the tool a folder name (an S3 key prefix). It lists every object under that prefix in the configured S3 bucket and downloads each one. It returns all of the files' contents in one formatted text block, with file name, last-modified time and size shown for each.

**Key points** (details in [Section 6](#6-nuances)):

- The bucket is fixed in code. You pass only the folder name, not a bucket or a full S3 URI ([6.1](#61-folder-name-is-a-prefix-in-a-fixed-bucket)).
- Files over 1 MB are not downloaded, and binary files are not decoded. Both show a marker in place of their content ([6.2](#62-large-and-binary-files-are-not-returned)).
- Sub-folders are included. Every object whose key starts with the prefix is returned ([6.3](#63-the-read-is-recursive)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`folder_name`**
```
incoming/reports
```

### 2.2 Calling the tool in an agent

`folder_name` changes on every call. The bucket and region are fixed in code, and access comes from the pod's IAM role, so the agent passes neither.

```
folder_name = {{folder_name}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | str | ✓ | Folder (key prefix) in the configured S3 bucket whose files should be read, e.g. `incoming/reports`. Leading and trailing `/` are stripped and a single trailing `/` is added. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| AWS credentials | Pod Identity (IAM role on the pod) | There are no keys in code or in Secrets Manager. boto3 resolves the pod's role. The role needs `s3:ListBucket` and `s3:GetObject` on the bucket. |
| `BUCKET_NAME` | Code — `S3DocumentRetriever` | `SETUP-REQUIRED:` placeholder `<your-s3-bucket-name>`. Replace it with the bucket to read from. |
| `AWS_REGION` | Code — `S3DocumentRetriever` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the bucket's region. |
| `MAX_FILE_BYTES` | Code — `S3DocumentRetriever` | Defaults to `1_000_000` bytes. Files larger than this are skipped. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-s3-reader.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `boto3` | `boto3` | S3 client |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |

---

## 6. Nuances

### 6.1 Folder name is a prefix in a fixed bucket
The tool always reads from `BUCKET_NAME`. `folder_name` is treated as a key prefix, so `s3://bucket/path` or a bucket name in the value is not understood and returns no files. **Do:** pass only the path inside the bucket, e.g. `incoming/reports`.

### 6.2 Large and binary files are not returned
Objects larger than `MAX_FILE_BYTES` (1 MB) are not downloaded. Their body shows `[SKIPPED: file exceeds size limit]`. Objects that are not valid UTF-8 (PDF, images, archives) show `[BINARY OR NON-UTF8 CONTENT: <n> bytes]`. **Do:** use this tool for text files only, and check for these markers before passing the content on.

### 6.3 The read is recursive
Every object whose key starts with `<folder_name>/` is returned, including objects in sub-folders, sorted by key. Zero-byte "folder marker" objects are skipped. **Do:** point the tool at the narrowest folder you need so large trees are not pulled into the agent's context.

### 6.4 A failed file does not stop the read
If one file fails to download, its body shows `[READ_FAILED: <error>]` and the other files are still returned. **Do:** search the output for `READ_FAILED` when completeness matters.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `s3:ListObjectsV2` (paginated) | List every object under the prefix |
| 2 | `s3:GetObject` (per object ≤ 1 MB) | Download each file's content |

### 7.2 Returns

**Success**
```
FILE_SOURCE: S3
BUCKET: <bucket-name>
FOLDER: <prefix>/
FILE_COUNT: <n>

===== FILE: <key> =====
LAST_MODIFIED: <timestamp>
SIZE_BYTES: <size>

<file content | [SKIPPED: file exceeds size limit] | [READ_FAILED: <error>] | [BINARY OR NON-UTF8 CONTENT: <n> bytes]>
```

**Error**
```
<ERROR_CODE>: <detail>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `S3_CLIENT_INIT_FAILED` | The boto3 S3 client could not be created (e.g. invalid region) | Check `AWS_REGION` |
| `S3_LIST_FAILED` | Listing failed: bucket missing, access denied, or no credentials on the pod | Check `BUCKET_NAME`, the Pod Identity association, and `s3:ListBucket` on the role |
| `S3_RETRIEVE_FAILED: No files found under folder '<prefix>'` | Nothing exists under the prefix | Check the folder name and its case |

### 7.3 Known limitations

- Read-only. It cannot write, overwrite or delete objects.
- Reads one bucket, set in code. There is no parameter to choose the bucket or region.
- No filter by file type, date or name pattern. Everything under the prefix is returned.
- No option to change the 1 MB limit or to stop recursion into sub-folders.
- Text only. Binary formats are not parsed or extracted.

### 7.4 Security & resilience

**Security**
- No credentials are stored in code. Access comes from the pod's IAM role through Pod Identity, so permissions are controlled entirely by that role's policy.
- Error strings include the raw boto3 exception text, which may show bucket or key names.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | No explicit timeout; boto3 defaults apply | Set a `botocore.config.Config` with connect and read timeouts |
| Retry | boto3 default retry mode only; no tool-level retry | Use `retries={"mode": "standard"}` in the client config |
| Concurrency | Files are downloaded one at a time | Use a bounded thread pool for large folders |
| Input validation | `folder_name` is only stripped of `/`; an empty value becomes the prefix `/` and returns `S3_RETRIEVE_FAILED` | Reject empty folder names with a clear message |
