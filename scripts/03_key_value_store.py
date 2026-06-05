import json
import asyncio
import railtracks as rt

from rich import print
from railtracks.llm import MessageHistory, UserMessage, AssistantMessage, SystemMessage

from amygdala.agent import SimpleAgent, KeyValueAgent
from amygdala.memory import KeyValueStore


_opener = """
Welcome! You can start chatting.
(type `quit` to exit)\n
User:
"""

_closer = """\nAssistant:
Goodbye!
"""


async def run_agent():
    store = KeyValueStore()
    state = store.get_state()

    user_msg: str = input(_opener)
    resp = None
    msg_history = MessageHistory()

    # NOTE: Proper Context Injection?
    if state:
        mem_context = f"## What you know about the user:\n{json.dumps(state, indent=2)}"
        msg_history.append(SystemMessage(mem_context))

    while True:
        # Process the latest user message
        if user_msg.strip().lower() == "quit":
            print(_closer)
            break
        msg_history.append(UserMessage(user_msg))

        # Get the response from assistant
        resp = await rt.call(SimpleAgent, msg_history)
        msg_history.append(AssistantMessage(resp.content))
        print(f"\nAssistant:\n{resp.content}")

        # Key-Value Stuff
        state = store.get_state()
        mem_msg = f"user: {user_msg}\nassistant: {resp.content}\ncurrent state: {state}"
        ops = await rt.call(KeyValueAgent, mem_msg)
        store.apply_operations(ops.structured)

        # Get new user message
        user_msg = input("\nUser:\n")

    return resp


if __name__ == "__main__":
    resp = asyncio.run(run_agent())
    if resp is not None:
        print(f"\nMessage History:\n{resp.message_history}")
