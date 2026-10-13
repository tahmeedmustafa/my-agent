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

tools = {"get_time": get_time, "add_numbers": add_numbers}

SYSTEM = {"role": "system", "content": "Only use get_time when asked the time. Only use add_numbers when asked to add numbers. For everything else, answer normally without tools."}

MEMORY_FILE = "memory.json"
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE) as f:
        memory = json.load(f)
else:
    memory = []
history = [SYSTEM] + memory

while True:
    msg = input("You: ")
    if msg == "bye":
        break
    history.append({"role": "user", "content": msg})
    while True:
        reply = ollama.chat(model="llama3.2", messages=history, tools=list(tools.values()))
        history.append(reply.message)
        if not reply.message.tool_calls:
            break
        for call in reply.message.tool_calls:
            name = call.function.name
            args = call.function.arguments
            print(f"[tool] {name}({args})")
            try:
                result = tools[name](**args)
            except Exception as e:
                result = f"Tool error: {e}"
            history.append({"role": "tool", "content": str(result), "tool_name": name})
    print("Agent:", reply.message.content)
    memory.append({"role": "user", "content": msg})
    memory.append({"role": "assistant", "content": reply.message.content})
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)