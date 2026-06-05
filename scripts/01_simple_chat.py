import asyncio
import railtracks as rt

from rich import print
from railtracks.llm import MessageHistory, UserMessage, AssistantMessage

from amygdala.agent import SimpleAgent


_opener = """
Welcome! You can start chatting.
(type `quit` to exit)\n
User:
"""

_closer = """\nAssistant:
Goodbye!
"""


async def run_agent():
    user_msg: str = input(_opener)
    resp = None
    msg_history = MessageHistory()

    while True:
        if user_msg.strip().lower() == "quit":
            print(_closer)
            break
        msg_history.append(UserMessage(user_msg))
        resp = await rt.call(SimpleAgent, msg_history)
        msg_history.append(AssistantMessage(resp.content))

        print(f"\nAssistant:\n{resp.content}")

        user_msg = input("\nUser:\n")

    return resp


if __name__ == "__main__":
    resp = asyncio.run(run_agent())
    if resp is not None:
        print(f"\nMessage History:\n{resp.message_history}")
