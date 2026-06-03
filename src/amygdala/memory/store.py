import json

from uuid import uuid4
from pathlib import Path
from railtracks.llm import Message

from .schema import Session, StoredMessage, MemoryOperations


_CONV_PATH = Path("records/conversation.json")
_KV_PATH = Path("records/memory.json")


# ===== Conversation Store =====


class ConversationStore:
    def __init__(self, path: Path = _CONV_PATH):
        self.path = path
        self._sessions: list[Session] = []
        self._load()

    # ====== Persistence
    def _load(self) -> None:
        if self.path.exists():
            raw = json.loads(self.path.read_text())
            self._sessions = [Session(**s) for s in raw]

    def _save(self) -> None:
        self.path.write_text(
            json.dumps([s.model_dump() for s in self._sessions], indent=4)
        )

    # ===== Public API
    def new_session(self) -> Session:
        session = Session(session_id=str(uuid4()))
        self._sessions.append(session)
        return session

    def add_message(self, session: Session, message: Message) -> None:
        session.messages.append(
            StoredMessage(role=message.role, content=message.content)
        )
        self._save()

    def all_sessions(self) -> list[Session]:
        return self._sessions

    def last_n_messages(self, n: int | None = None) -> list[StoredMessage]:
        all_messages = [msg for session in self._sessions for msg in session.messages]
        return all_messages if n is None else all_messages[-n:]


# ===== Key-Value Store =====


class KeyValueStore:
    def __init__(self, path: Path = _KV_PATH) -> None:
        self.path = path
        self.data = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            self.data = json.loads(self.path.read_text())

    def _save(self):
        self.path.write_text(json.dumps(self.data, indent=4))

    def apply_operations(self, ops: MemoryOperations):
        for op in ops.operations:
            if op.action == "save" and op.value is not None:
                self.data[op.key] = op.value
            elif op.action == "delete":
                self.data.pop(op.key, None)
        self._save()

    def get_state(self):
        return self.data
