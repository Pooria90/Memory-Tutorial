import json

from uuid import uuid4
from pathlib import Path

from railtracks.llm import Message
from railtracks.retrieval.embedding import OpenAIEmbedding
from railtracks.retrieval import Chunk, EmbeddedChunk
from railtracks.retrieval.stores import VectorStore, ChromaBackend, StoreEntry, StoreQuery

from .schema import Session, StoredMessage, MemoryOperations


_CONV_PATH = Path("records/conversation.json")
_KV_PATH = Path("records/memory.json")
_VS_PATH = Path("records/memory")


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

    # ===== Persistence
    def _load(self) -> None:
        if self.path.exists():
            self.data = json.loads(self.path.read_text())

    def _save(self):
        self.path.write_text(json.dumps(self.data, indent=4))

    # ===== Public API
    def apply_operations(self, ops: MemoryOperations):
        for op in ops.operations:
            if op.action == "save" and op.value is not None:
                self.data[op.key] = op.value
            elif op.action == "delete":
                self.data.pop(op.key, None)
        self._save()

    def get_state(self):
        return self.data


# ===== Vector Store =====

class AmygdalaVectorStore:
    def __init__(self, vs: VectorStore, embedding_model: str = "text-embedding-3-small") -> None:
        self.model = embedding_model
        self.embedder = OpenAIEmbedding(model=embedding_model)
        self.vs = vs

    @classmethod
    async def create(cls, embedding_model: str = "text-embedding-3-small") -> "AmygdalaVectorStore":
        backend = await ChromaBackend.create("amygdala_db", path=str(_VS_PATH))
        return cls(VectorStore(backend), embedding_model)

    # ===== Internal tools
    async def _convert_str_to_entry(self, content: str):
        vector = await self._extract_embedding(content)
        _id = uuid4()
        return StoreEntry(
            content=content,
            vector=vector,
            id=_id,
            chunk_id=_id,
            document_id=_id,
            embedding_model=self.model
        )

    async def _convert_str_to_query(self, content: str, top_k: int = 3):
        return StoreQuery(
            text=content,
            embedding=await self._extract_embedding(content),
            top_k=top_k
        )

    async def _extract_embedding(self, content: str):
        embeddings = await self.embedder.aembed([content])
        return embeddings.vectors[0]

    # ===== Public API
    async def record(self, content: str) -> None:
        entry = await self._convert_str_to_entry(content=content)
        await self.vs.write(entry)

    async def ask(self, content: str, top_k: int = 3) -> list[str]:
        query = await self._convert_str_to_query(content=content, top_k=top_k)
        results = await self.vs.read(query)
        return [r.entry.content for r in results]


#TODO: Build one purely based on Chroma