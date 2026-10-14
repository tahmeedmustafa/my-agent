import ollama
import json
import os
from datetime import datetime

def get_time():
    """Get the current date and time."""
    return datetime.now().strftime("%A %d %B %Y, %I:%M %p")

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return int(a) + int(b)

def save_note(text: str) -> str:
    """Save a note so it can be read later."""
    with open("notes.txt", "a") as f:
        f.write(text + "\n")
    return "Note saved."

def read_notes() -> str:
    """Read all saved notes."""
    if not os.path.exists("notes.txt"):
        return "No notes yet."
    with open("notes.txt") as f:
        return f.read()

def read_file(filename: str) -> str:
    """Read a text file from the agent's folder."""
    name = os.path.basename(filename)
    if not os.path.exists(name):
        return f"No file called {name}."
    with open(name) as f:
        return f.read()[:3000]

def write_file(filename: str, text: str) -> str:
    """Write text into a file in the agent's folder."""
    name = os.path.basename(filename)
    if name in ("agent.py", "memory.json"):
        return f"Not allowed to change {name}."
    with open(name, "w") as f:
        f.write(text)
    return f"Wrote {name}."

tools = {"get_time": get_time, "add_numbers": add_numbers, "save_note": save_note, "read_notes": read_notes, "read_file": read_file, "write_file": write_file}

NEEDS_APPROVAL = ["write_file"]

SYSTEM = {"role": "system", "content": "Only use get_time when asked the time. Only use add_numbers when asked to add numbers. Use save_note when asked to note or remember something. Use read_notes when asked about notes. Use read_file when asked to read or open a file. Use write_file when asked to create or write a file. For everything else, answer normally without tools."}

def log(name, args, result):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now():%Y-%m-%d %H:%M} {name}({args}) -> {str(result)[:100]}\n")

MEMORY_FILE = "memory.json"
MEMORY_LIMIT = 20
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE) as f:
        memory = json.load(f)
else:
    memory = []
history = [SYSTEM] + memory[-MEMORY_LIMIT:]

MAX_STEPS = 5

while True:
    msg = input("You: ")
    if msg == "bye":
        break
    history.append({"role": "user", "content": msg})
    for step in range(MAX_STEPS):
        reply = ollama.chat(model="llama3.2", messages=history, tools=list(tools.values()))
        history.append(reply.message)
        if not reply.message.tool_calls:
            break
        for call in reply.message.tool_calls:
            name = call.function.name
            args = call.function.arguments
            print(f"[tool] {name}({args})")
            if name in NEEDS_APPROVAL:
                ok = input("Allow? y/n: ")
                if ok.lower() != "y":
                    result = "DENIED. The user said no. The file was NOT written. Tell the user you did not do it."
                    log(name, args, result)
                    history.append({"role": "tool", "content": result, "tool_name": name})
                    continue
            try:
                result = tools[name](**args)
            except Exception as e:
                result = f"Tool error: {e}"
            log(name, args, result)
            history.append({"role": "tool", "content": str(result), "tool_name": name})
    text = reply.message.content or "(Stopped: too many tool calls.)"
    print("Agent:", text)
    memory.append({"role": "user", "content": msg})
    memory.append({"role": "assistant", "content": text})
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)