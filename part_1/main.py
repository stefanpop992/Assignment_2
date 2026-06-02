import time
import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY saknas. Lägg den i .env-filen.")

client = OpenAI(api_key=api_key)


SYSTEM_PROMPT = """
You are a simple ReAct software engineering agent.

You may only help with safe software engineering tasks.

You can either request a bash command or give a final answer.

When you want to run a bash command, answer exactly like this:

THOUGHT: short reason
ACTION: bash
COMMAND: command_here

When you are done, answer exactly like this:

FINAL: your answer here

Rules:
- Use only raw text output.
- Do not use JSON.
- Do not use markdown.
- Do not use function calling or tools.
- You may only request safe bash commands.
- Do not ask for dangerous commands such as rm, sudo, chmod, chown, shutdown, reboot, mkfs, dd, curl, wget.
- Prefer safe commands such as ls, pwd, cat, python3.
"""


def is_safe_command(command: str) -> bool:
    dangerous = [
        "rm",
        "sudo",
        "chmod",
        "chown",
        "shutdown",
        "reboot",
        "mkfs",
        "dd",
        ":(){",
        "curl",
        "wget"
    ]

    for word in dangerous:
        if word in command:
            return False

    return True


def run_bash(command: str) -> str:
    print(f"\n[Agent vill köra bash]: {command}")

    if not is_safe_command(command):
        return "Command blocked because it may be dangerous."

    confirm = input("Vill du köra detta kommando? (y/n): ").strip().lower()

    if confirm != "y":
        return "Command was not executed because the user denied it."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stdout + result.stderr

        if output.strip() == "":
            output = "[No output]"

        if len(output) > 2000:
            output = output[:2000] + "\n...[output truncated]"

        return output

    except subprocess.TimeoutExpired:
        return "Command stopped because it took too long."

    except Exception as e:
        return f"Error while running command: {e}"


def parse_agent_response(response: str):
    action = None
    command = None
    final = None

    for line in response.splitlines():
        line = line.strip()

        if line.startswith("ACTION:"):
            action = line.replace("ACTION:", "", 1).strip()

        elif line.startswith("COMMAND:"):
            command = line.replace("COMMAND:", "", 1).strip()

        elif line.startswith("FINAL:"):
            final = line.replace("FINAL:", "", 1).strip()

    return action, command, final


def ask_openai(messages: list) -> str:
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )

            text = response.choices[0].message.content

            if text:
                return text

            return "FINAL: OpenAI returned an empty response."

        except Exception as e:
            print(f"\n[OpenAI API error, attempt {attempt + 1}/3]")
            print(e)

            if attempt < 2:
                print("Väntar 3 sekunder och testar igen...")
                time.sleep(3)

    return "FINAL: OpenAI API failed after 3 attempts. Try running the program again."


def main():
    user_task = input("Vad vill du att agenten ska göra? ")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_task}
    ]

    max_steps = 5

    for step in range(max_steps):
        print(f"\n--- Agent steg {step + 1} ---")

        agent_response = ask_openai(messages)

        print("\n[AI svar - rå text]")
        print(agent_response)

        action, command, final = parse_agent_response(agent_response)

        print("\n[DEBUG parsed]")
        print("Action:", action)
        print("Command:", command)
        print("Final:", final)

        messages.append({"role": "assistant", "content": agent_response})

        if action == "bash" and command:
            tool_result = run_bash(command)

            print("\n[Tool result]")
            print(tool_result)

            messages.append({
                "role": "user",
                "content": (
                    f"Tool result from bash command: {command}\n\n"
                    f"Output:\n{tool_result}\n\n"
                    "Continue. If you have enough information, answer with FINAL:"
                )
            })

        elif final:
            print("\n[FINAL]")
            print(final)
            break

        else:
            print("\nKunde inte förstå AI-svaret.")
            break

    else:
        print("\nMax antal steg nåddes. Stoppar agenten.")


if __name__ == "__main__":
    main()
