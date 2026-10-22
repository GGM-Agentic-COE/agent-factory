# tool-L0-s3-writer

## 1. Executive summary

You give the tool a folder name (an S3 key prefix), a file name and some text. It writes the text as a UTF-8 object at `<folder_name>/<file_name>` in the configured S3 bucket. It returns a dictionary with the status, the object key, the size written and the upload time.

**Key points** (details in [Section 6](#6-nuances)):

- The file is stored under the exact name given. An existing object with the same key is overwritten without warning ([6.1](#61-existing-files-are-overwritten)).
- The bucket is fixed in code, and any path in `file_name` is stripped to its last segment ([6.2](#62-folder-and-file-name-handling)).
- Content over 1 MB (UTF-8 encoded) is rejected, and every object is stored as `text/plain` ([6.3](#63-size-limit-and-content-type)).

---

## 2. How to use

### 2.1 Calling the tool in aava

Enter these values and click **Execute**.

**`folder_name`**
```
exec-20261021-0001
```

**`file_name`**
```
summary.md
```

**`contents`**
```
# Summary

All checks passed.
```

### 2.2 Calling the tool in an agent

All three parameters change per call. `folder_name` is usually a workflow identifier; `file_name` and `contents` usually come from what the agent produced earlier. The bucket and region are fixed in code, and access comes from the pod's IAM role, so the agent passes neither.

```
folder_name = {{workflow_execution_id}}
file_name = summary.md
contents = the full content the agent produced, verbatim
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | str | ✓ | Folder (key prefix) in the configured S3 bucket to upload into, e.g. a workflow execution id. Leading and trailing `/` are stripped and a single trailing `/` is added. |
| `file_name` | str | ✓ | Exact name of the file to create, e.g. `summary.md`. Only the part after the last `/` is used. Must not be empty after stripping. |
| `contents` | str | ✓ | Text to write. Encoded as UTF-8; at most `MAX_FILE_BYTES` (1,000,000) bytes after encoding. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| AWS credentials | Pod Identity (IAM role on the pod) | There are no keys in code or in Secrets Manager. boto3 resolves the pod's role. The role needs `s3:PutObject` on the bucket. |
| `BUCKET_NAME` | Code — `S3UploadTool` | `SETUP-REQUIRED:` placeholder `<your-s3-bucket-name>`. Replace it with the bucket to write to. |
| `AWS_REGION` | Code — `S3UploadTool` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the bucket's region. |
| `MAX_FILE_BYTES` | Code — `S3UploadTool` | Defaults to `1_000_000` bytes. Larger content is rejected. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-s3-writer.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `boto3` | `boto3` | S3 client |
| `botocore.exceptions` | `botocore` | `ClientError` handling on upload |
| `datetime` | stdlib | UTC upload timestamp |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |

---

## 6. Nuances

### 6.1 Existing files are overwritten
The object key is exactly `<folder_name>/<file_name>`; no timestamp or suffix is added. If an object with that key already exists, `put_object` replaces it and the tool still returns `SUCCESS`. **Do:** use a unique `folder_name` (e.g. the workflow execution id) or a unique `file_name` when earlier versions must be kept.

### 6.2 Folder and file name handling
The tool always writes to `BUCKET_NAME`. `folder_name` is a key prefix, so `s3://` URIs or bucket names in it end up as part of the key. `file_name` is reduced to its last path segment, so `reports/q3/summary.md` is written as `<folder_name>/summary.md`. An empty or slash-only `file_name` returns `INVALID_FILE_NAME`. **Do:** put the full path inside the bucket in `folder_name` (e.g. `exec-123/reports`) and only the bare file name in `file_name`.

### 6.3 Size limit and content type
`contents` is encoded as UTF-8 and rejected with `FILE_TOO_LARGE` if it exceeds 1,000,000 bytes. Every object is stored with `ContentType` `text/plain; charset=utf-8`, whatever the file extension. **Do:** split large outputs into several files, and do not use this tool for binary data or where a specific content type is needed.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `s3:PutObject` | Write the UTF-8 content to `<folder_name>/<file_name>` |

### 7.2 Returns

**Success**
```
{
  "status": "SUCCESS",
  "bucket": "<bucket-name>",
  "key": "<folder>/<file_name>",
  "file_name": "<file_name>",
  "folder": "<folder>/",
  "size_bytes": <n>,
  "uploaded_at": "<YYYYMMDD_HHMMSS>"
}
```

**Error**
```
{"status": "FAILED", "reason": "<ERROR_CODE>: <detail>"}
```

| Error | Cause | Fix |
|-------|-------|-----|
| `S3_CLIENT_INIT_FAILED: <detail>` | The boto3 S3 client could not be created (e.g. invalid region) | Check `AWS_REGION` |
| `INVALID_FILE_NAME` | `file_name` was empty or only slashes | Pass a bare file name such as `summary.md` |
| `FILE_TOO_LARGE: <n> bytes exceeds limit of 1000000` | Encoded `contents` is over `MAX_FILE_BYTES` | Split the content into smaller files |
| `S3_UPLOAD_FAILED (<code>): <message>` | S3 rejected the write, e.g. `AccessDenied` or `NoSuchBucket` | Check `BUCKET_NAME`, the Pod Identity association, and `s3:PutObject` on the role |
| `S3_UPLOAD_FAILED: <detail>` | Any other upload error, e.g. no credentials on the pod or a network failure | Check the Pod Identity association and network access to S3 |

### 7.3 Known limitations

- Write-only. It cannot read, list or delete objects.
- Writes to one bucket, set in code. There is no parameter to choose the bucket or region.
- No option to skip or fail when the object already exists; it always overwrites.
- Text only. Content type is always `text/plain; charset=utf-8`, and there is no option to set metadata, tags, storage class or encryption settings.
- No option to change the 1 MB limit.

### 7.4 Security & resilience

**Security**
- No credentials are stored in code. Access comes from the pod's IAM role through Pod Identity, so permissions are controlled entirely by that role's policy.
- `file_name` is reduced to its basename, so a caller cannot write outside `folder_name` through the file name. `folder_name` itself is not restricted, so any prefix the role allows can be written to.
- Error strings include the S3 error code and message or the raw boto3 exception text, which may show bucket or key names.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | No explicit timeout; boto3 defaults apply | Set a `botocore.config.Config` with connect and read timeouts |
| Retry | boto3 default retry mode only; no tool-level retry | Use `retries={"mode": "standard"}` in the client config |
| Concurrency | One object per call; concurrent calls with the same key overwrite each other (last write wins) | Use unique folder or file names per workflow run |
| Input validation | Empty `file_name` and content over 1 MB are rejected; `folder_name` is only stripped of `/`, so an empty value writes to the key `/<file_name>` | Reject empty folder names with a clear message |
