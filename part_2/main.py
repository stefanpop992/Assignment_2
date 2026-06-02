import os
import json
import time
import subprocess
from dotenv import load_dotenv
from openai import OpenAI 


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY saknas. Lägg den i .env-filen.")

client = OpenAI(api_key=api_key)

MAX_TOOL_OUTPUT = 2000


def load_system_prompt(path: str = "system_prompt.txt") -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(script_dir, path)
    with open(full_path, "r", encoding="utf-8") as file:
        return file.read()


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
        "wget",
        "mv /",
        ">/dev",
    ]

    for word in dangerous:
        if word in command:
            return False

    return True


def limit_output(output: str) -> str:
    if output.strip() == "":
        return "[No output]"

    if len(output) > MAX_TOOL_OUTPUT:
        return output[:MAX_TOOL_OUTPUT] + "\n...[tool output truncated]"

    return output


def run_bash(command: str) -> str:
    print(f"\n[Agent vill köra bash]: {command}")

    if not is_safe_command(command):
        return "Command blocked because it may be dangerous."

    confirm = input("Vill du köra detta kommando? (y/n): ").strip().lower()

    if confirm not in ["y", "yes", "j", "ja"]:
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
        return limit_output(output)

    except subprocess.TimeoutExpired:
        return "Command stopped because it took too long."

    except Exception as e:
        return f"Error while running command: {e}"


def is_safe_path(path: str) -> bool:
    if path.startswith("/"):
        return False

    if ".." in path:
        return False

    return True


def edit_file(path: str, old_text: str, new_text: str) -> str:
    print(f"\n[Agent vill editera fil]: {path}")

    if not is_safe_path(path):
        return "File edit blocked because the path is unsafe."

    confirm = input("Vill du ändra denna fil? (y/n): ").strip().lower()

    if confirm not in ["y", "yes", "j", "ja"]:
        return "File edit was not executed because the user denied it."

    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

        if old_text not in content:
            return "File edit failed because old_text was not found in the file."

        new_content = content.replace(old_text, new_text, 1)

        with open(path, "w", encoding="utf-8") as file:
            file.write(new_content)

        return f"File edit successful. Replaced text in {path}."

    except FileNotFoundError:
        return f"File edit failed because file was not found: {path}"

    except Exception as e:
        return f"File edit error: {e}"


def parse_json_response(response: str) -> dict:
    try:
        return json.loads(response)

    except json.JSONDecodeError:
        cleaned = response.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned.replace("```json", "", 1).strip()

        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```", "", 1).strip()

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {
                "type": "final",
                "answer": "Could not parse model response as JSON."
            }


def ask_openai(prompt: str) -> str:
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        if response.output_text:
            return response.output_text

        return '{"type": "final", "answer": "OpenAI returned an empty response."}'

    except Exception as e:
        return json.dumps({
            "type": "final",
            "answer": f"OpenAI API error: {e}"
        })


def build_conversation(system_prompt: str, session_history: list) -> str:
    conversation = system_prompt + "\n\n"

    for item in session_history:
        conversation += f"{item['role'].upper()}:\n{item['content']}\n\n"

    return conversation


def main():
    system_prompt = load_system_prompt()

    user_task = input("Vad vill du att agenten ska göra? ")

    session_history = [
        {
            "role": "user",
            "content": user_task
        }
    ]

    max_steps = 8

    for step in range(max_steps):
        print(f"\n--- Agent steg {step + 1} ---")

        conversation = build_conversation(system_prompt, session_history)
        agent_response = ask_openai(conversation)

        print("\n[AI raw response]")
        print(agent_response)

        parsed = parse_json_response(agent_response)

        print("\n[Parsed JSON]")
        print(parsed)

        session_history.append({
            "role": "assistant",
            "content": agent_response
        })

        response_type = parsed.get("type")

        if response_type == "final":
            print("\n[FINAL]")
            print(parsed.get("answer", "No final answer provided."))
            break

        elif response_type == "tool_call":
            tool_name = parsed.get("tool")

            if tool_name == "bash":
                command = parsed.get("command", "")
                tool_result = run_bash(command)

            elif tool_name == "edit_file":
                path = parsed.get("path", "")
                old_text = parsed.get("old_text", "")
                new_text = parsed.get("new_text", "")

                tool_result = edit_file(path, old_text, new_text)

            else:
                tool_result = f"Unknown tool: {tool_name}"

            print("\n[Tool result]")
            print(tool_result)

            session_history.append({
                "role": "tool",
                "content": tool_result
            })

        else:
            print("\nKunde inte förstå response type.")
            break

    else:
        print("\nMax antal steg nåddes. Stoppar agenten.")


if __name__ == "__main__":
    main()