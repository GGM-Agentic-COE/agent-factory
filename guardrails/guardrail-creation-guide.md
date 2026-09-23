# Guardrail Authoring Guide
How to create the `.co` and `.yml` files for a NeMo guardrail.

---

## What you need before starting

From your guardrail spec, identify:

- **Name** — the `gr-L{n}-{name}` identifier
- **Layer** — L1 / L2 / L3 / L4 and its scope
- **Trigger** — `input` or `output`
- **Category** — short slug e.g. `secrets`, `pii`, `misogyny`
- **Severity** — `critical`, `high`, or `medium`
- **Reason** — one sentence describing what was blocked
- **What to detect** — the list of things to flag
- **Carve-outs** — what must never be flagged

---

## The .co file

The `.co` file tells NeMo what to return when the guardrail fires. It always has exactly three `define bot` blocks, all returning the same JSON payload.

```
# {guardrail-name} — Prompt-Only Mode
# Layer: {layer}
# Triggers on: {input/output}

define bot refuse to respond
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"{input/output}\"}"

define bot inform cannot answer
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"{input/output}\"}"

define bot inform answer unknown
  "{\"detected\": true, \"verdict\": \"rejected\", \"reason\": \"{reason}\", \"severity\": \"{severity}\", \"category\": \"{category}\", \"rail\": \"{input/output}\"}"

```

**Rules:**
- All three blocks return the same JSON — do not vary them
- Leave a blank line after the last block
- Never add a `define flow` block

---

## The .yml file

The `.yml` file has three sections: `models`, `rails`, and `prompts`.

```yaml
models:

  - type: main
    engine: openai
    model: gpt-5.4


rails:
  {input/output}:
    flows:
      - self check {input/output}

prompts:
  - task: self_check_{input/output}
    content: |
      Your task is to check if the {bot response/user input} contains {one-line description}.

      {Bot response/User input}: "{{ {bot_response/user_input} }}"

      Flag ONLY if the {response/input} contains {category noun} such as:
      1. {first item with example}
      2. {second item with example}

      Do NOT flag:
      - {first carve-out}
      - {second carve-out}

      Answer only "yes" if the {response/input} is safe and contains no {category noun}.
      Answer "no" if the {response/input} contains {category noun}.
```

**Rules:**
- Blank line after `models:`, two blank lines after `model: gpt-5.4` — spacing matters
- No `parameters` block — omit temperature and max_tokens entirely
- `type` is always `main`
- For output rails: task `self_check_output`, placeholder `{{ bot_response }}`, label `Bot response:`
- For input rails: task `self_check_input`, placeholder `{{ user_input }}`, label `User input:`
- `Flag ONLY if` uses numbered list, `Do NOT flag` uses bullets
- `yes` = safe (passes), `no` = blocked — never invert
- Answer lines always use `Answer only "yes"` and `Answer "no"` — exact wording

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| `type: self_check_output` | Always `type: main` |
| Adding `parameters:` block | Remove it entirely |
| Adding `define flow` to the `.co` | Remove it — NeMo handles routing |
| `Answer yes` instead of `Answer only "yes"` | Match wording exactly |
| Missing blank lines in `.yml` | One after `models:`, two after `model: gpt-5.4` |
| Missing trailing blank line in `.co` | Add one after the last `define bot` block |