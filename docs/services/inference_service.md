# Inference Service

## File: `src/services/inference.py`

This module provides a unified interface for interacting with various Large Language Models (LLMs).

## Protocol: `InferenceServiceProtocol`

Defines the contract that all inference services must follow.

*   `get_summary(content: str, max_words: int) -> str`
*   `get_structured_output(content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]`

## Class: `GeminiService`

Implementation of `InferenceServiceProtocol` using Google's Gemini API.

### Configuration
*   Requires `GEMINI_API_KEY` environment variable.
*   Uses `gemini-2.5-flash` model by default.

### Key Methods

#### `get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]`
Generates a structured JSON response from the LLM based on a provided schema.

*   **Process:**
    1.  Constructs a prompt including the JSON schema and the content.
    2.  Calls the Gemini API.
    3.  Parses the response text to extract the JSON object.
    4.  Handles potential JSON parsing errors.

#### `get_summary(self, content: str, max_words: int = 100) -> str`
Generates a text summary of the provided content.

## Other Implementations

The module also contains (or is designed to support) other implementations like:
*   `OllamaService`: For local LLM inference (e.g., Llama 2, Mistral).
*   `OpenAIService`: For OpenAI's GPT models.
*   `ModelInferenceService`: A wrapper or base class for model interactions.
