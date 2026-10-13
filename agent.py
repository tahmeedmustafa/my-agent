import ollama
from datetime import datetime

def get_time():
    """Get the current date and time."""
    return datetime.now().strftime("%A %d %B %Y, %I:%M %p")

def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return int(a) + int(b)

tools = {"get_time": get_time, "add_numbers": add_numbers}
history = []

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
            result = tools[name](**args)
            history.append({"role": "tool", "content": str(result), "tool_name": name})
    print("Agent:", reply.message.content)