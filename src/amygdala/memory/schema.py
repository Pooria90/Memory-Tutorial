from datetime import datetime, timezone
from pydantic import BaseModel, Field
from typing import Literal


# ===== Data Models for Episodic Memory =====

class StoredMessage(BaseModel):
    role: str
    content: str


class Session(BaseModel):
    session_id: str
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    messages: list[StoredMessage] = Field(default_factory=list)


# ===== Data Models for Semantic Memory =====

class MemoryOperation(BaseModel):
    action: Literal["save", "delete"]
    key: str
    value: str


class MemoryOperations(BaseModel):
    operations: list[MemoryOperation]


# ===== Data Models for Vector Memory =====

class ExtractedFacts(BaseModel):
    facts: list[str] = Field(default_factory=list)
