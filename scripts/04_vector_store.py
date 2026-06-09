import asyncio
import railtracks as rt

from rich import print
from railtracks.llm import MessageHistory, UserMessage, AssistantMessage, SystemMessage

from amygdala.agent import SimpleAgent, VectorMemoryAgent
from amygdala.memory import AmygdalaVectorStore


_opener = """
Welcome! You can start chatting.
(type `quit` to exit)\n
User:
"""

_closer = """\nAssistant:
Goodbye!
"""

_TOP_K = 3


def _build_history(turns: list[tuple[str, str]], recalled: list[str]) -> MessageHistory:
    history = MessageHistory()
    if recalled:
        facts_text = "\n".join(f"- {f}" for f in recalled)
        history.append(SystemMessage(f"## What you know about the user:\n{facts_text}"))
    for role, content in turns:
        if role == "user":
            history.append(UserMessage(content))
        else:
            history.append(AssistantMessage(content))
    return history


async def run_agent():
    vs = await AmygdalaVectorStore.create()

    user_msg: str = input(_opener)
    resp = None
    turns: list[tuple[str, str]] = []

    while True:
        if user_msg.strip().lower() == "quit":
            print(_closer)
            break

        # Retrieve facts semantically relevant to this message before responding
        recalled = await vs.ask(user_msg, top_k=_TOP_K)
        turns.append(("user", user_msg))

        resp = await rt.call(SimpleAgent, _build_history(turns, recalled))
        turns.append(("assistant", resp.content))

        print(f"\nAssistant:\n{resp.content}")

        # Extract and store new facts from this exchange
        mem_input = f"user: {user_msg}\nassistant: {resp.content}"
        facts_resp = await rt.call(VectorMemoryAgent, mem_input)
        for fact in facts_resp.structured.facts:
            await vs.record(fact)

        if recalled:
            print(f"\n[dim][Recalled {len(recalled)} fact(s): {recalled}][/dim]")
        if facts_resp.structured.facts:
            print(f"[dim][Stored {len(facts_resp.structured.facts)} new fact(s): {facts_resp.structured.facts}][/dim]")

        user_msg = input("\nUser:\n")

    return resp


if __name__ == "__main__":
    resp = asyncio.run(run_agent())
    if resp is not None:
        print(f"\nMessage History:\n{resp.message_history}")
