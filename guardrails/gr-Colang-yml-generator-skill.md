---
name: guardrail-prompt-writer
description: Use this skill whenever the user pastes a guardrail description or README and asks for the .co and .yml files. Generates both files printed as plain text code blocks in chat. Generalised for any guardrail type.
trigger: When the user pastes a guardrail spec, README, or description and asks to create or generate the .co and .yml files for it.
---

# Guardrail Prompt Writer Skill

When the user provides a guardrail description, generate exactly two files printed as plain text code blocks in the chat response. Never use create_file, present_files, or artifacts. Never add explanation between the files unless asked.

Print the `.co` file first, labelled with its filename. Then the `.yml` file, labelled with its filename.

---

## Step 1 — Extract from the user's description

Read the user's guardrail description and extract these fields before writing anything:

| Field | Where to find it |
|-------|-----------------|
| `guardrail-name` | The `gr-L{n}-{name}` identifier |
| `layer` | L1 / L2 / L3 / L4 and scope description |
| `triggers-on` | input / output |
| `category` | Short slug for JSON payload e.g. `secrets`, `pii`, `misogyny` |
| `severity` | `critical` / `high` / `medium` |
| `reason` | Human-readable sentence describing what was blocked |
| `what-to-detect` | The numbered list of things to flag |
| `do-not-flag` | The explicit carve-outs |

If any field is missing, infer it from context. Do not ask clarifying questions.

---

## Step 2 — Write the .co file

Use this exact format. Substitute fields from Step 1.

```
# {guardrail-name} — Prompt-Only Mode
# Layer: {layer}
# Triggers on: {triggers-on}

define bot refuse to respond
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"{triggers-on}\"}"

define bot inform cannot answer
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"{triggers-on}\"}"

define bot inform answer unknown
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"{triggers-on}\"}"

```

### .co Rules
- Always exactly three `define bot` blocks in this order: `refuse to respond`, `inform cannot answer`, `inform answer unknown`
- All three return the same JSON string
- Leave a blank line after the last block
- Never add `define flow` or anything else

---

## Step 3 — Write the .yml file

Use this exact format. Substitute fields from Step 1.

```yaml
models:

  - type: main
    engine: openai
    model: gpt-5.4


rails:
  {triggers-on}:
    flows:
      - self check {triggers-on}

prompts:
  - task: self_check_{triggers-on}
    content: |
      Your task is to check if the {bot response/user input} contains {one-line description of what this guardrail detects}.

      {Bot response/User input}: "{{ {bot_response/user_input} }}"

      Flag ONLY if the {response/input} contains {category noun} such as:
      1. {first detection item with example}
      2. {second detection item with example}
      ... {continue for all items from the guardrail description}

      Do NOT flag:
      - {first carve-out}
      - {second carve-out}
      ... {continue for all carve-outs from the guardrail description}

      Answer only "yes" if the {response/input} is safe and contains no {category noun}.
      Answer "no" if the {response/input} contains {category noun}.
```

### .yml formatting rules
- Blank line after `models:` before the list item
- Two blank lines between `model: gpt-5.4` and `rails:` — this matches the working format exactly
- No `temperature` or `max_tokens` lines — omit the `parameters` block entirely
- `type` is always `main`
- `engine` is always `openai`
- `model` is always `gpt-5.4`
- For output rails: task is `self_check_output`, placeholder is `{{ bot_response }}`, label is `Bot response:`
- For input rails: task is `self_check_input`, placeholder is `{{ user_input }}`, label is `User input:`
- Flow name matches: `self check output` or `self check input` (spaces, NeMo built-in)

### Prompt rules
- One-line task description only — no preamble
- `Flag ONLY if` uses numbered items (1. 2. 3.)
- `Do NOT flag` uses bullet points (-)
- No few-shot examples
- No chain-of-thought instructions
- Last two lines are always the yes/no answer instruction
- `yes` = safe (no violation), `no` = blocked — never invert
- Answer lines use `Answer only "yes"` and `Answer "no"` — match this wording exactly

---

## Common Errors — Never Do These

| Error | Rule |
|-------|------|
| `type:` anything other than `main` | Always `type: main` |
| Including `parameters:` block | Omit entirely — no temperature or max_tokens |
| Adding `define flow` to the .co | Never |
| Few-shot examples in the prompt | Never |
| Inverting yes/no | yes = safe, no = blocked |
| Missing blank lines in .yml | Two blank lines after model, one after `models:` |
| Missing trailing blank line in .co | Always leave one blank line after the last define block |
