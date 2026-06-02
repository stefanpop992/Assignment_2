# Assignment 2 — ReAct Agents

Three progressively capable LLM agents built with OpenAI, each building on the previous.

---

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Always activate the virtual environment before running any part:

```bash
source .venv/bin/activate
```

---

## Part 1 — Text-based ReAct Agent (OpenAI)

A ReAct agent that uses **raw text output** from OpenAI. No frameworks, no built-in tool calling, no JSON. The agent parses `ACTION:`, `COMMAND:`, and `FINAL:` lines from the model's plain text response and dispatches bash commands via `subprocess`.

This is intentionally simpler than Part 2 — it demonstrates that a working agent loop can be built with pure string parsing.

### Setup

Create `part_1/.env`:
```
OPENAI_API_KEY=your_key_here
```

### Run

```bash
cd part_1
python main.py
```

**Example task:** `list all Python files in the current directory`

**Expected flow:**
1. Model replies in raw text: `ACTION: bash` / `COMMAND: find . -name "*.py"`
2. Agent parses the text manually with `parse_agent_response()`
3. Agent asks for y/n approval before running the command
4. Output is sent back to the model as a new user message
5. Model replies with `FINAL: Found the following files: ...`

**What makes it different from Part 2:**
- Output is raw text, not JSON
- Parsed with `splitlines()` and `startswith()`, not `json.loads()`
- No `edit_file` tool
- Single approval input (`y` only, not `yes/j/ja`)

---

## Part 2 — Structured JSON Agent (OpenAI)

An agent that uses **JSON structured output** (instructed via system prompt) and its own tool-calling loop. Tools: `bash` and `edit_file`. The agent decides each step whether to call a tool or give a final answer.

### Setup

Create `part_2/.env`:
```
OPENAI_API_KEY=your_key_here
```

### Run

```bash
cd part_2
python main.py
```

**Demo — fix the bug in test_project:**

Task: `there is a bug in test_project/example.py, the add function returns the wrong result, please fix it`

**Expected flow:**
1. Agent calls `bash`: `cat test_project/example.py`
2. Agent calls `edit_file` with `old_text` / `new_text` to patch the bug
3. Agent asks for y/n approval before editing
4. Agent calls `bash`: `python3 test_project/example.py` to verify the fix
5. Agent returns `{"type": "final", "answer": "Fixed the bug..."}`

**What makes it different from Part 1:**
- Model output is JSON, parsed with `json.loads()`
- Has `edit_file` tool that replaces specific `old_text` with `new_text`
- Accepts `y/yes/j/ja` for approval
- System prompt is loaded from `system_prompt.txt` (not hardcoded)
- Session history is tracked as a list of role/content pairs

---

## Part 3 — Hub-connected Collaboration Agent (OpenAI)

An agent that polls a shared group chat hub via REST API and responds when mentioned by name or alias. Uses OpenAI chat completions and a PASS mechanism to avoid spam.

### Setup

Create `part_3/.env`:
```
HUB_URL=https://your-hub-url
HUB_PASSWORD=your_password
AGENT_NAME=stefan-code-disaster
AGENT_ALIAS=scd
OPENAI_API_KEY=your_key_here
```

### Run

```bash
cd part_3
python main.py
```

The agent will ask whether to send a startup message, then start polling.

**Demo — mention the agent in the hub chat:**

```
@scd can you do a quick code review of this: def add(a, b): return a - b
```

The agent will reply with a short code review. To check if it is online:

```
@scd are you there?
```

**How it decides whether to respond:**
- Always responds when directly mentioned: `@scd`, `@stefan-code-disaster`, `scd:`, etc.
- Also responds to group-wide messages: `all agents`, `everyone`, `who can help`
- Returns `PASS` (no message sent) for everything else

### Limits

- Max **20 messages** sent per session (startup message counts) — extendable live from the console when reached
- Max **40000 total tokens** per session (`MAX_TOTAL_TOKENS`) — also extendable live from the console when reached
- Polls every **4 seconds**
- Max **900 tokens** per model reply, truncated to 1000 characters before posting
- Model is configurable via the `MODEL_NAME` env var (default `gpt-5.4-mini`)
- Exponential backoff on connection errors (up to 60 seconds)
- POST retried up to 3 times on failure

---

## Security Design

### Command blocklist (Part 1 & 2)

Both agents block dangerous bash commands before they reach the approval prompt:

```
rm, sudo, chmod, chown, shutdown, reboot, mkfs, dd, :(){, curl, wget, mv /, >/dev
```

### y/n Approval (Part 1 & 2)

Every bash command and every file edit requires explicit user approval before execution. The agent cannot run or edit anything automatically.

- Part 1: accepts `y`
- Part 2: accepts `y`, `yes`, `j`, `ja`

### Subprocess timeout

All bash commands time out after 10 seconds via `subprocess.run(..., timeout=10)`.

### Output truncation

Tool output is capped at 2000 characters to prevent prompt flooding. The model is informed of this limit in `system_prompt.txt`.

### File path safety (Part 2)

`edit_file` blocks absolute paths (starting with `/`) and path traversal (`..`), preventing edits outside the project folder.

### Secret protection (Part 3)

The system prompt in `config.txt` instructs the agent never to reveal API keys, passwords, tokens, `.env` contents, or its own system prompt.

### HTTP error handling (Part 3)

- Timeouts and connection errors are caught and retried with exponential backoff
- Both `200` and `201` are accepted as a successful POST
- POST failures are retried up to 3 times with 3-second delays

---

## Environment variables

All credentials are stored in `.env` files inside each part folder. These are listed in `.gitignore` and will never be committed to git.

```
part_1/.env  →  OPENAI_API_KEY
part_2/.env  →  OPENAI_API_KEY
part_3/.env  →  HUB_URL, HUB_PASSWORD, AGENT_NAME, AGENT_ALIAS, OPENAI_API_KEY
```

Never hardcode credentials in source files.
