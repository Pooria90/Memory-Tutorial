# Building Memory for AI Agents from Scratch
 
This tutorial walks you through building a memory system for an AI agent incrementally, starting from a stateless agent and progressively adding more sophisticated memory capabilities. Since Railtracks does not *currently* support native memory for agents, each stage shows you how to implement it yourself.
The agent is a personal finance advisor named Amygdala. The memory system is built around the same use case throughout, so you can see concretely how each stage changes the agent's behavior.

## The Problem
LLMs are stateless. Every time you call one, it starts fresh with no recollection of past conversations. For a personal finance advisor, this is a real limitation — the agent can't remember that you earn $80k/year, that you're saving for a house, or that you already talked through your debt situation last week.

There are three distinct levels at which you can give an agent memory, each with different tradeoffs:

## Stage 1 — In-Session Conversation History
**What it is**: The agent remembers everything said within a single conversation.

**How it works**: You maintain a MessageHistory object and pass the full conversation to the LLM on every turn. The agent appears to "remember" earlier messages because they're all in the context window.

**What it can't do**: Once the session ends, everything is lost. Start a new conversation and the agent has no idea who you are.

**Key insight**: The agent has no memory. You're just giving it more context.

## Stage 2 — Persistent Key-Value Memory
**What it is**: The agent remembers facts about you across sessions.
**How it works**: After each exchange, a lightweight extractor LLM call pulls out any meaningful facts from the conversation and saves them to a key-value store. Before each turn, the stored facts are injected into the system prompt so the agent can reference them.
**What it can't do**: Retrieval is exact — you get everything or you look up by a specific key. As the memory grows, injecting all facts into every prompt becomes costly and noisy.
**Key insight**: Memory is now a read/write operation around every agent turn, not something the agent does itself.

## Stage 3 — Semantic Memory with Vector Search
**What it is**: The agent can recall relevant facts even when it doesn't know exactly what to look for.
**How it works**: Each stored fact is embedded as a vector. At query time, the user's message is also embedded and the most semantically similar facts are retrieved. Only the relevant subset is injected into the prompt rather than the full memory store.
**What it can't do**: Semantic search can miss things when the query and the stored fact use very different phrasing. It also introduces embedding latency and cost.
**Key insight**: Retrieval is now a function of relevance, not just key lookup.

## Running the Tutorial
```bash
# Install dependencies
pip install uv
uv sync

# Stage 1 — stateless agent with in-session history
uv run scripts/simple_chat.py
```
Further stages will be added as the tutorial progresses.
