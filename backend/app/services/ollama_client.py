"""Ollama chat client.

Thin wrapper around Ollama's /api/chat endpoint. Kept separate from the
answer-generation logic so it can be mocked in tests without needing a
real Ollama server running.
"""

import httpx

from app.core.config import settings


class OllamaUnavailableError(Exception):
    """Raised when Ollama can't be reached or returns an error."""


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: int) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def chat(self, system_prompt: str, user_prompt: str) -> str:
        """Send a system + user message to Ollama, return the reply text."""
        try:
            response = httpx.post(
                f"{self._base_url}/api/chat",
                json={
                    "model": self._model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "stream": False,
                    "options": {"num_predict": 600},
                },
                timeout=self._timeout_seconds,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaUnavailableError(
                f"Could not reach Ollama at {self._base_url}. Make sure Ollama "
                f"is running and the '{self._model}' model has been pulled. "
                f"({exc})"
            ) from exc

        data = response.json()
        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise OllamaUnavailableError(
                f"Unexpected response shape from Ollama: {data}"
            ) from exc


ollama_client = OllamaClient(
    settings.ollama_base_url, settings.llm_model, settings.ollama_timeout_seconds
)
