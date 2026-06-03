from datetime import datetime, timezone
from pydantic import BaseModel, Field


class StoredMessage(BaseModel):
    role: str
    content: str


class Session(BaseModel):
    session_id: str
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    messages: list[StoredMessage] = Field(default_factory=list)
