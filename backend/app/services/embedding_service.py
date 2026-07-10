"""Embedding generation via BAAI/bge-m3.

Uses sentence-transformers, which BGE-M3's model card documents as a
supported way to get its dense embedding output (the model also supports
sparse/ColBERT modes, but this project only uses dense — matching the
`vector(1024)` column in the Supabase schema).

The model is loaded lazily on first use, not at import time, so:
- the app can start without network access / a downloaded model,
- tests can monkeypatch `embed_texts` without ever touching the real model.
"""

from app.core.config import settings


class EmbeddingService:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Return one dense embedding vector per input text, in order."""
        if not texts:
            return []
        model = self._load_model()
        vectors = model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()


embedding_service = EmbeddingService(settings.embedding_model)
