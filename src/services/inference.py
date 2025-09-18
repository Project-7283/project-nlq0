import os
import requests
import json
from typing import Optional, Dict, Any
from typing import Protocol, List

from src.models.model import Model

class GeminiService:
    """
    Service class for interacting with Google Gemini LLM.
    Exposes methods for summarization, structured output, intent analysis, and general chat completion.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiService.")

    def _call_gemini(self, prompt: str) -> str:
        """
        Private method to send a prompt to the Gemini API and handle the response.
        """
        headers = {
            "Content-Type": "application/json",
        }
        params = {
            "key": self.api_key
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, params=params, json=data)
            response.raise_for_status()  # This will raise an HTTPError for bad responses (4xx or 5xx)
            
            response_json = response.json()
            
            # The structure of the Gemini API response is nested
            return response_json['candidates'][0]['content']['parts'][0]['text']
            
        except requests.exceptions.HTTPError as err:
            print(f"HTTP Error: {err}")
            print(f"Response content: {err.response.text}")
            return "An error occurred during the API call."
        except (KeyError, IndexError) as err:
            print(f"Parsing Error: Could not find expected keys in the Gemini response. {err}")
            return "An error occurred while parsing the API response."
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
            return "An unexpected error occurred."

    def get_summary(self, content: str, max_words: int = 100) -> str:
        """
        Generates a summary of the provided content.
        """
        prompt = f"""
        Summarize the following text in under {max_words} words.

        Text:
        {content}
        
        Summary:
        """
        return self._call_gemini(prompt)

    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts structured data from content based on a JSON schema.
        """
        schema_str = json.dumps(json_schema, indent=2)
        prompt = f"""
        Extract information from the following text based on the provided JSON schema. 
        The final output MUST be a valid JSON object that adheres to this schema.

        Schema:
        {schema_str}

        Text:
        {content}

        Output JSON:
        """

        # print("debug prompt\n----------\n", prompt)
        
        json_string = self._call_gemini(prompt)
        
        try:
            # Attempt to parse the string output from the model into a JSON object
            return json.loads(json_string.strip('```json\n').strip('```').strip())
        except json.JSONDecodeError:
            print("Error: The model did not return a valid JSON object.", json_string)
            return {}

    def analyze_intent(self, query: str) -> str:
        """
        Analyzes the intent of a user query and returns a single word/phrase.
        """
        prompt = f"""
        Analyze the intent of the following user query. Respond with a single word or a short phrase that best describes the intent, such as 'booking', 'information', 'purchase', 'complaint', 'technical support'. Do not include any other text or punctuation.

        Query:
        {query}

        Intent:
        """
        return self._call_gemini(prompt).strip()

    def chat_completion(self, message: str, context: Optional[str] = None) -> str:
        """
        Provides a general chat completion response.
        """
        if context:
            prompt = f"Context: {context}\n\nUser: {message}"
        else:
            prompt = f"User: {message}"
            
        return self._call_gemini(prompt)

class InferenceServiceProtocol(Protocol):
    def get_summary(self, content: str, max_words: int = 100) -> str: ...
    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]: ...
    def analyze_intent(self, query: str) -> str: ...
    def chat_completion(self, message: str, context: Optional[str] = None) -> str: ...

class ModelInferenceService:
    """
    Generic inference service using a Model instance (OpenAI-compatible).
    Exposes the same protocol as GeminiService.
    """
    def __init__(self, model: Optional[Model] = None):
        self.model: Model = model or Model(api_base="http://127.0.0.1:1234/v1", model_name="google/gemma-3-4b", api_key="nt-required")

    def get_summary(self, content: str, max_words: int = 100) -> str:
        prompt = f"""
        Summarize the following text in under {max_words} words.

        Text:
        {content}

        Summary:
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.model.chat(messages)
        # Try to extract summary from response
        if isinstance(response, dict):
            return response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return str(response).strip()

    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        schema = {
            "name": "extracted_data",
            "schema": json_schema
        }
        prompt = f"""
        Extract information from the following text based on the provided JSON schema.
        The final output MUST be a valid JSON object that adheres to this schema.

        Schema:
        {json.dumps(json_schema, indent=2)}

        Text:
        {content}

        Output JSON:
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.model.chat(
            messages,
            response_format="json_schema",
            json_schema=schema
        )
        # Try to extract JSON from response
        try:
            if isinstance(response, str):
                return json.loads(response.strip())
            else:
                return response
        except Exception as e:
            print("Error parsing structured output:", e)
            return {}

    def analyze_intent(self, query: str) -> str:
        prompt = """
        Analyze the intent of the following user query. Respond with a single word or a short phrase that best describes the intent, such as 'booking', 'information', 'purchase', 'complaint', 'technical support'. Do not include any other text or punctuation.

        Query:
        %s

        Intent:
        """ % query
        messages = [{"role": "user", "content": prompt}]
        response = self.model.chat(messages)
        if isinstance(response, dict):
            return response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return str(response).strip()

    def chat_completion(self, message: str, context: Optional[str] = None) -> str:
        if context:
            prompt = f"Context: {context}\n\nUser: {message}"
        else:
            prompt = f"User: {message}"
        messages = [{"role": "user", "content": prompt}]
        response = self.model.chat(messages)
        if isinstance(response, dict):
            return response.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        return str(response).strip()