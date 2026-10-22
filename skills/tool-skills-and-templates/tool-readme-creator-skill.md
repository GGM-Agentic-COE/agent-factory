---
name: tool-readme-writer
description: Write or rewrite the README for a CrewAI BaseTool in this tools/ folder (tool-L0-*). Use whenever a tool README is created, rewritten, or brought back in line with the tool's current code. Follows TOOL_README_TEMPLATE.md exactly and derives every statement from the code.
---

# Tool README writer

Writes `tool-L0-<name>-README.md` for one tool folder, following
[TOOL_README_TEMPLATE.md](TOOL_README_TEMPLATE.md) exactly. Every README is
written from scratch from the **current code**. Old READMEs are out of date and
must not be used as a source.

## Inputs to read first

1. Every `.py` file in the tool folder. Each tool normally has one `.py` file,
   which is the **production file**. Where a folder has more than one, the production file is the one
   containing `secrets-manager` in its name.
   Credentials come either from AWS Secrets Manager (an `AWSSecretReaderPodIdentity`
   class with a `SECRET_NAME`) or straight from Pod Identity (no secret, the boto3
   default chain). Document whichever the code actually does.
2. The tool's `-spec.yaml`, if it exists, for naming and layer only. Never copy its
   behaviour claims without checking them against the code.
3. This skill's `TOOL_README_TEMPLATE.md`.

Do **not** read the existing README for content. Delete it and write a new one.

## Hard rules

- **Structure.** Use the template's headings, numbering, order, separators (`---`)
  and table columns exactly as written. Do not add, rename, merge or reorder
  sections. Delete only the `{{…}}` placeholder text and the template's guidance
  sentences inside `{{…}}`. Keep the fixed sentences such as "Enter these values and click **Execute**."
- **Title.** `# tool-L0-<name>`, matching the folder name. Never write L1.
- **Source of truth is the code.** Document parameters, defaults, return strings,
  error strings, API calls, limits and behaviour only when you can see them in the
  production file. Quote return or error strings exactly as the code builds them.
  If something is unknown, say so; never guess.
- **No secret names or environment identifiers.** Never write a real Secrets
  Manager secret name, bucket, account URL, org, token or key. Refer to the secret
  as "the secret named in `SECRET_NAME`" and show placeholders exactly as they
  appear in the code (e.g. `<name-of-secret-in-aws-secrets-manager>`).
- **Section 1 key points** link to the matching Section 6 nuances. 2 to 4 bullets.
- **Section 2.1** shows realistic example values for every parameter in the
  args schema, one block per parameter, in schema order. Omit optional parameters
  only if the example is clearer without them; say so.
- **Section 2.2** names which parameters the agent supplies per call and which are
  fixed. Use `{{variable}}` placeholders for workflow values.
- **Section 3** lists every field of the args schema: exact name, Python type, ✓ for
  required, blank for optional, plus default and accepted values in the description.
- **Section 4** lists every value read from the secret (its key name in the secret
  dict) and every `SETUP-REQUIRED:` value in code. For Pod Identity-only tools, the
  Source column says "Pod Identity (IAM role on the pod)" and names the IAM actions needed. End with the template sentence,
  naming the production file.
- **Section 5** lists only modules actually imported by the production file, with
  their pip package (standard library: `stdlib`).
- **Section 6** covers behaviour that changes how a user or agent must call the tool
  (input formats, overwrite or skip behaviour, size limits, pagination, format
  conversion, partial-failure handling). Each one is a short paragraph ending
  in **Do:**.
- **Section 7.1** lists the external API or SDK calls in the order the code makes them,
  starting with the Secrets Manager read.
- **Section 7.2** shows the success output shape and every error string the code can
  return or raise.
- **Section 7.3** lists only what the tool cannot do by design.
- **Section 7.4** describes timeouts, retries, concurrency and input validation *as
  implemented* (state "None" when absent) with a concrete recommendation.
- Plain, client-ready language. No internal notes, history, TODOs or "FIX" remarks.

## Companion spec.yaml (same pass)

When the README changes, check the tool's `-spec.yaml` agrees with it: same
`metadata.name`, `layer: L0`, parameters, returns and security notes. Bump
`metadata.version` when behaviour changes.

## Output

Write the README to `<tool-folder>/tool-L0-<name>-README.md`, replacing any
existing file. Then check it against the template, heading by heading.
