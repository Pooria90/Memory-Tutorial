import asyncio
import railtracks as rt

from rich import print
from railtracks.llm import (
    MessageHistory,
    UserMessage,
    AssistantMessage
)

from amygdala.agent import SimpleAgent
from amygdala.memory import Session, ConversationStore


_opener = """
Welcome! You can start chatting.
(type `quit` to exit)\n
User:
"""

_closer = """\nAssistant:
Goodbye!
"""

_HISTORY_WINDOW = 20


def _load_history(store: ConversationStore) -> MessageHistory:
    history = MessageHistory()
    for msg in store.last_n_messages(_HISTORY_WINDOW):
        if msg.role == "user":
            history.append(UserMessage(msg.content))
        else:
            history.append(AssistantMessage(msg.content))
    return history


async def run_agent():
    store = ConversationStore()
    session = store.new_session()

    user_msg: str = input(_opener)
    resp = None
    msg_history = _load_history(store)

    while True:
        if user_msg.strip().lower() == "quit":
            print(_closer)
            break
        msg_history.append(
            UserMessage(user_msg)
        )

        if store:
            store.add_message(session, UserMessage(user_msg))

        resp = await rt.call(SimpleAgent, msg_history)
        msg_history.append(
            AssistantMessage(resp.content)
        )

        if store:
            store.add_message(session, AssistantMessage(resp.content))

        print(f"\nAssistant:\n{resp.content}")

        user_msg = input("\nUser:\n")

    return resp



if __name__ == "__main__":
    resp = asyncio.run(run_agent())
    if resp is not None:
        print(f"\nMessage History:\n{resp.message_history}")
