import railtracks as rt

from .messages import SIMPLE_SYSTEM_PROMPT


_llm = rt.llm.AnthropicLLM("claude-sonnet-4-6")


# ====== 1. Simple QA
SimpleAgent = rt.agent_node(
    name="Simple-Agent", llm=_llm, system_message=SIMPLE_SYSTEM_PROMPT
)
