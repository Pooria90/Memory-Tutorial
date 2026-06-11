import railtracks as rt

from ..memory.store import AmygdalaVectorStore


_TOP_K = 3

_store: AmygdalaVectorStore | None = None


async def _get_store() -> AmygdalaVectorStore:
    global _store
    if _store is None:
        _store = await AmygdalaVectorStore.create()
    return _store


@rt.function_node
async def save_memory(fact: str) -> str:
    """Save one fact about the user to long-term memory.

    Args:
        fact: A standalone, self-contained sentence describing a single fact
            about the user, with specific numbers and timeframes when known
            (e.g. "The user has $10,000 in credit card debt at 20% APR.").

    Returns:
        A confirmation that the fact was stored.
    """
    store = await _get_store()
    await store.record(fact)
    return f"Stored: {fact}"


@rt.function_node
async def recall_memories(query: str) -> str:
    """Search long-term memory for facts about the user relevant to a query.

    Args:
        query: A natural-language description of what you want to know about
            the user (e.g. "income, savings goals and debts").

    Returns:
        The most relevant stored facts, or a message saying nothing was found.
    """
    store = await _get_store()
    facts = await store.ask(query, top_k=_TOP_K)
    if not facts:
        return "No relevant memories found."
    return "\n".join(f"- {f}" for f in facts)
