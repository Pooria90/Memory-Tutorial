import railtracks as rt

from .messages import SIMPLE_SYSTEM_PROMPT, KEY_VALUE_SYSTEM_PROMPT
from ..memory.schema import MemoryOperations

_main_llm = rt.llm.AnthropicLLM("claude-sonnet-4-6")
_memory_llm = rt.llm.AnthropicLLM("claude-haiku-4-5")


# ===== Simple QA ======

SimpleAgent = rt.agent_node(
    name="Simple-Agent", llm=_main_llm, system_message=SIMPLE_SYSTEM_PROMPT
)


# ===== Key-Value Manager =====

KeyValueAgent = rt.agent_node(
    name="Key-Value-Agent",
    llm=_memory_llm,
    system_message=KEY_VALUE_SYSTEM_PROMPT,
    output_schema=MemoryOperations,
)
