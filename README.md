# Building Memory for AI Agents from Scratch
 
This tutorial walks you through building a memory system for an AI agent incrementally, starting from a stateless agent and progressively adding more sophisticated memory capabilities. Since Railtracks does not *currently* support native memory for agents, each stage shows you how to implement it yourself.
The agent is a personal finance advisor named Amygdala. The memory system is built around the same use case throughout, so you can see concretely how each stage changes the agent's behavior.

## The Problem
LLMs are stateless. Every time you call one, it starts fresh with no recollection of past conversations. For a personal finance advisor, this is a real limitation — the agent can't remember that you earn $80k/year, that you're saving for a house, or that you already talked through your debt situation last week.

There are several distinct levels at which you can give an agent memory, each with different tradeoffs:

## Stage 1 — In-Session Conversation History
**What it is**: The agent remembers everything said within a single conversation.

**How it works**: You maintain a MessageHistory object and pass the full conversation to the LLM on every turn. The agent appears to "remember" earlier messages because they're all in the context window.

**What it can't do**: Once the session ends, everything is lost. Start a new conversation and the agent has no idea who you are.

**Key insight**: The agent has no memory. You're just giving it more context.

## Stage 2 — Persistent Conversation History
**What it is**: The agent remembers past conversations by replaying their transcripts.
**How it works**: Every message is written to a ConversationStore on disk. When a new session starts, previous transcripts are loaded back into the context window before the conversation begins.
**What it can't do**: It doesn't scale. The context grows without bound, and the agent has to wade through everything ever said to find the one fact that matters.
**Key insight**: Persistence alone isn't memory — replaying raw history just delays the problem.

## Stage 3 — Persistent Key-Value Memory
**What it is**: The agent remembers facts about you across sessions.
**How it works**: After each exchange, a lightweight extractor LLM call pulls out any meaningful facts from the conversation and saves them to a key-value store. Before each turn, the stored facts are injected into the system prompt so the agent can reference them.
**What it can't do**: Retrieval is exact — you get everything or you look up by a specific key. As the memory grows, injecting all facts into every prompt becomes costly and noisy.
**Key insight**: Memory is now a read/write operation around every agent turn, not something the agent does itself.

## Stage 4 — Semantic Memory with Vector Search
**What it is**: The agent can recall relevant facts even when it doesn't know exactly what to look for.
**How it works**: Each stored fact is embedded as a vector. At query time, the user's message is also embedded and the most semantically similar facts are retrieved. Only the relevant subset is injected into the prompt rather than the full memory store.
**What it can't do**: Semantic search can miss things when the query and the stored fact use very different phrasing. It also introduces embedding latency and cost.
**Key insight**: Retrieval is now a function of relevance, not just key lookup.

## Stage 5 — Agentic Memory with Tools
**What it is**: The agent manages its own memory. It decides what is worth remembering and when to look something up.
**How it works**: The vector store is exposed to the agent as two tools — `save_memory` and `recall_memories`. Nothing is wrapped around the conversation loop anymore: no extractor call after each exchange, no forced retrieval before each response. The agent calls the tools mid-turn whenever it judges it needs to.
**What it can't do**: Recall is only as reliable as the agent's judgment — it may not think to search memory when it should. Production systems often keep automatic retrieval for reads and reserve tools for writes.
**Key insight**: Memory is no longer plumbing around the agent — it's an action the agent takes.

## Running the Tutorial
```bash
# Install dependencies
pip install uv
uv sync

# Stage 1 — stateless agent with in-session history
uv run scripts/01_simple_chat.py

# Stage 2 — persistent conversation history
uv run scripts/02_simple_chat_history.py

# Stage 3 — key-value fact memory
uv run scripts/03_key_value_store.py

# Stage 4 — semantic memory with vector search
uv run scripts/04_vector_store.py

# Stage 5 — agentic memory with tools
uv run scripts/05_agentic_memory.py
```
Stages 1–3 need an `ANTHROPIC_API_KEY`; stages 4–5 also need an `OPENAI_API_KEY` for embeddings.
