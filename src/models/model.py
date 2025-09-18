from datetime import datetime
import os
import requests
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class Model:
    """
    Represents an LLM model interface, wrapping OpenAI-compatible API calls.
    Supports structured output, tools, schema-guided prompting, and embeddings.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        embed_model: Optional[str] = None,
    ):
        self.api_base = api_base or os.getenv("LLM_API_BASE")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.model = model_name or os.getenv("LLM_MODEL")
        self.embed_model = embed_model or os.getenv("LLM_EMBED_MODEL") or self.model

        if not all([self.api_base, self.api_key, self.model]):
            raise ValueError(
                "Missing LLM config: ensure API base, key, and model are provided or in env vars"
            )

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        messages: List[Dict[str, str]],
        response_format: str = "",
        temperature: float = 0.2,
        json_schema: Optional[Dict] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
    ) -> Any:
        """
        Calls the LLM chat endpoint with optional schema or tool calling.
        """
        payload: Dict[str, Any] = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": f"Current Date Time: {datetime.now()}"}
            ]
            + messages,
        }

        if response_format == "json":
            payload["response_format"] = {"type": "json"}

        elif response_format == "json_schema":
            if not json_schema:
                raise ValueError(
                    "JSON Schema must be provided when using response_format 'json_schema'"
                )
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": json_schema.get("name", "response"),
                    "schema": json_schema["schema"],
                    "strict": True,
                },
            }

        if tools:
            payload["tools"] = tools
            if tool_choice:
                payload["tool_choice"] = tool_choice

        response = requests.post(
            f"{self.api_base}/chat/completions", json=payload, headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of input texts.

        Args:
            texts (list[str]): Input texts for embedding.

        Returns:
            list[list[float]]: Corresponding list of embedding vectors.
        """
        payload = {"input": texts, "model": self.embed_model}

        print(f"[Model Embedding] Requesting embeddings for {len(texts)} texts.")
        response = requests.post(
            f"{self.api_base}/embeddings", json=payload, headers=self.headers
        )
        response.raise_for_status()
        data = response.json()

        return [entry["embedding"] for entry in data.get("data", [])]
