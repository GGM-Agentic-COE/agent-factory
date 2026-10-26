# tool-L0-s3-files-reader

## 1. Executive summary

You give the tool a folder name (an S3 key prefix) and a list of file names. It looks up each named file in that folder of the configured S3 bucket and downloads it. It returns the contents of all requested files in one formatted text block, with last-modified time and size for each file it found, and a marker for each file it could not read.

**Key points** (details in [Section 6](#6-nuances)):

- The bucket is fixed in code. You pass only the folder name and bare file names, not a bucket, S3 URI or sub-path ([6.1](#61-folder-and-file-name-handling)).
- Missing or unreadable files do not stop the read; each one gets a marker. The call only fails when no file could be read at all ([6.2](#62-partial-results-and-markers)).
- Files over 1 MB are not downloaded, and binary files are not decoded ([6.3](#63-large-and-binary-files-are-not-returned)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`folder_name`**
```
exec-20261021-0001
```

**`file_names`**
```
["summary.md", "findings.md"]
```

### 2.2 Calling the tool in an agent

Both parameters change per call. `folder_name` is usually the workflow identifier used when the files were written; `file_names` lists the files the agent needs. The bucket and region are fixed in code, and access comes from the pod's IAM role, so the agent passes neither.

```
folder_name = {{workflow_execution_id}}
file_names = ["summary.md", "findings.md"]
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_name` | str | ✓ | Folder (key prefix) in the configured S3 bucket, e.g. a workflow execution id. Leading and trailing `/` are stripped and a single trailing `/` is added. |
| `file_names` | List[str] | ✓ | File names to read from that folder, e.g. `["summary.md", "findings.md"]`. Must not be empty. Each name is reduced to the part after its last `/`. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| AWS credentials | Pod Identity (IAM role on the pod) | There are no keys in code or in Secrets Manager. boto3 resolves the pod's role. The role needs `s3:GetObject` on the bucket's objects. Add `s3:ListBucket` on the bucket so missing files report `[NOT_FOUND]` instead of `[READ_FAILED: 403]`. |
| `BUCKET_NAME` | Code — `S3SpecificFileReader` | `SETUP-REQUIRED:` placeholder `<your-s3-bucket-name>`. Replace it with the bucket to read from. |
| `AWS_REGION` | Code — `S3SpecificFileReader` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the bucket's region. |
| `MAX_FILE_BYTES` | Code — `S3SpecificFileReader` | Defaults to `1_000_000` bytes. Files larger than this are skipped. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-s3-files-reader.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `boto3` | `boto3` | S3 client |
| `botocore.exceptions` | `botocore` | `ClientError` handling on file lookup |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |

---

## 6. Nuances

### 6.1 Folder and file name handling
The tool always reads from `BUCKET_NAME`. Each object key is built as `<folder_name>/<file_name>`. Each file name is reduced to its last path segment, so `reports/summary.md` is looked up as `<folder_name>/summary.md`. A name that is empty or only slashes shows `[INVALID_FILE_NAME]`. **Do:** put the full path inside the bucket in `folder_name` (e.g. `exec-123/reports`) and only bare file names in `file_names`; read files from different sub-folders in separate calls.

### 6.2 Partial results and markers
Files are processed in the order given. A file that does not exist shows `[NOT_FOUND]`, and one that cannot be looked up or downloaded shows `[READ_FAILED: <error>]`; the other files are still returned. If none of the requested files could be read, the whole call returns `S3_RETRIEVE_FAILED: None of the requested files could be read under '<prefix>'`. `FILE_COUNT` in the header is the number of names requested, not the number found. **Do:** search the output for `NOT_FOUND`, `READ_FAILED` and `INVALID_FILE_NAME` when every file is required.

### 6.3 Large and binary files are not returned
Files larger than `MAX_FILE_BYTES` (1 MB) are not downloaded; their body shows `[SKIPPED: file exceeds size limit]`, and they do not count as read. Files that are not valid UTF-8 (PDF, images, archives) show `[BINARY OR NON-UTF8 CONTENT: <n> bytes]`. **Do:** use this tool for text files only, and check for these markers before passing the content on.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `s3:HeadObject` (per requested file) | Check the file exists and get its size and last-modified time |
| 2 | `s3:GetObject` (per file ≤ 1 MB) | Download the file's content |

### 7.2 Returns

**Success**
```
FILE_SOURCE: S3
BUCKET: <bucket-name>
FOLDER: <prefix>/
FILE_COUNT: <number of names requested>

===== FILE: <key> =====
LAST_MODIFIED: <timestamp>
SIZE_BYTES: <size>

<file content | [SKIPPED: file exceeds size limit] | [READ_FAILED: <error>] | [BINARY OR NON-UTF8 CONTENT: <n> bytes]>

===== FILE: <key> =====
[NOT_FOUND | READ_FAILED: <code or error>]

===== FILE: <name as given> =====
[INVALID_FILE_NAME]
```

**Error**
```
<ERROR_CODE>: <detail>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `S3_RETRIEVE_FAILED: No file names provided` | `file_names` was an empty list | Pass at least one file name |
| `S3_CLIENT_INIT_FAILED: <detail>` | The boto3 S3 client could not be created (e.g. invalid region) | Check `AWS_REGION` |
| `S3_RETRIEVE_FAILED: None of the requested files could be read under '<prefix>'` | Every file was missing, invalid, over 1 MB, or failed to read | Check the folder and file names and their case, the Pod Identity association, and `s3:GetObject` on the role |
| `[NOT_FOUND]` (per file) | No object at `<folder_name>/<file_name>` | Check the file name and its case |
| `[READ_FAILED: <code or error>]` (per file) | Lookup or download failed, e.g. `403` (access denied, or missing file without `s3:ListBucket`) or `NoSuchBucket` | Check `BUCKET_NAME` and the role's S3 permissions |
| `[INVALID_FILE_NAME]` (per file) | A file name was empty or only slashes | Pass bare file names such as `summary.md` |

### 7.3 Known limitations

- Read-only. It cannot write, overwrite or delete objects.
- Reads one bucket, set in code. There is no parameter to choose the bucket or region.
- Reads only files directly named in one folder per call; there is no listing, wildcard or name-pattern matching.
- No option to change the 1 MB limit.
- Text only. Binary formats are not parsed or extracted.

### 7.4 Security & resilience

**Security**
- No credentials are stored in code. Access comes from the pod's IAM role through Pod Identity, so permissions are controlled entirely by that role's policy.
- Each file name is reduced to its basename, so a caller cannot read outside `folder_name` through the file name. `folder_name` itself is not restricted, so any prefix the role allows can be read.
- Output includes S3 error codes or raw boto3 exception text, which may show bucket or key names.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | No explicit timeout; boto3 defaults apply | Set a `botocore.config.Config` with connect and read timeouts |
| Retry | boto3 default retry mode only; no tool-level retry | Use `retries={"mode": "standard"}` in the client config |
| Concurrency | Files are looked up and downloaded one at a time | Use a bounded thread pool for long file lists |
| Input validation | Empty `file_names` list and empty names are rejected; duplicate names are read twice; `folder_name` is only stripped of `/`, so an empty value becomes the prefix `/` | Reject empty folder names and de-duplicate file names |
