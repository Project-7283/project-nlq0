import os
import json
import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List, Protocol
from openai import OpenAI, AsyncOpenAI
from src.utils.logging import app_logger as logger, performance_logger
from src.utils.circuit_breaker import CircuitBreaker

# Define circuit breakers for different services
gemini_cb = CircuitBreaker(name="GeminiAPI", failure_threshold=3, recovery_timeout=60)
openai_cb = CircuitBreaker(name="OpenAIAPI", failure_threshold=3, recovery_timeout=60)
ollama_cb = CircuitBreaker(name="OllamaAPI", failure_threshold=5, recovery_timeout=30)

class InferenceServiceProtocol(Protocol):
    def get_summary(self, content: str, max_words: int = 100) -> str: ...
    async def get_summary_async(self, content: str, max_words: int = 100) -> str: ...
    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]: ...
    async def get_structured_output_async(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]: ...
    def analyze_intent(self, query: str) -> str: ...
    async def analyze_intent_async(self, query: str) -> str: ...
    def chat_completion(self, message: str, context: Optional[str] = None) -> str: ...
    async def chat_completion_async(self, message: str, context: Optional[str] = None) -> str: ...

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiService.")

    @gemini_cb
    async def _call_gemini_async(self, prompt: str) -> str:
        start_time = time.time()
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.api_url, headers=headers, params=params, json=data, timeout=30.0)
                response.raise_for_status()
                response_json = response.json()
                
                duration = time.time() - start_time
                performance_logger.info(f"Gemini API call completed in {duration:.2f}s")
                
                return response_json['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                logger.error(f"Gemini Async Error: {str(e)}")
                raise e

    @gemini_cb
    def _call_gemini(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        
        try:
            import requests
            response = requests.post(self.api_url, headers=headers, params=params, json=data, timeout=30.0)
            response.raise_for_status()
            response_json = response.json()
            return response_json['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            logger.error(f"Gemini Sync Error: {str(e)}")
            raise e

    async def get_summary_async(self, content: str, max_words: int = 100) -> str:
        prompt = f"Summarize the following text in under {max_words} words.\n\nText:\n{content}\n\nSummary:"
        return await self._call_gemini_async(prompt)

    def get_summary(self, content: str, max_words: int = 100) -> str:
        prompt = f"Summarize the following text in under {max_words} words.\n\nText:\n{content}\n\nSummary:"
        return self._call_gemini(prompt)

    async def get_structured_output_async(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_str = json.dumps(json_schema, indent=2)
        prompt = f"Extract information from the following text based on the provided JSON schema.\nSchema:\n{schema_str}\n\nText:\n{content}\n\nOutput JSON:"
        json_string = await self._call_gemini_async(prompt)
        try:
            return json.loads(json_string.strip('```json\n').strip('```').strip())
        except json.JSONDecodeError:
            logger.error(f"Gemini failed to return valid JSON: {json_string}")
            return {}

    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_str = json.dumps(json_schema, indent=2)
        prompt = f"Extract information from the following text based on the provided JSON schema.\nSchema:\n{schema_str}\n\nText:\n{content}\n\nOutput JSON:"
        json_string = self._call_gemini(prompt)
        try:
            return json.loads(json_string.strip('```json\n').strip('```').strip())
        except json.JSONDecodeError:
            logger.error(f"Gemini failed to return valid JSON: {json_string}")
            return {}

    async def analyze_intent_async(self, query: str) -> str:
        prompt = f"Analyze the intent of the following user query. Respond with a short phrase.\nQuery:\n{query}\n\nIntent:"
        return (await self._call_gemini_async(prompt)).strip()

    def analyze_intent(self, query: str) -> str:
        prompt = f"Analyze the intent of the following user query. Respond with a short phrase.\nQuery:\n{query}\n\nIntent:"
        return self._call_gemini(prompt).strip()

    async def chat_completion_async(self, message: str, context: Optional[str] = None) -> str:
        prompt = f"Context: {context}\n\nUser: {message}" if context else f"User: {message}"
        return await self._call_gemini_async(prompt)

    def chat_completion(self, message: str, context: Optional[str] = None) -> str:
        prompt = f"Context: {context}\n\nUser: {message}" if context else f"User: {message}"
        return self._call_gemini(prompt)

class OpenAIService:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIService.")
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.model = model

    @openai_cb
    async def _call_openai_async(self, messages: List[Dict[str, str]], response_format: Optional[Dict] = None) -> str:
        start_time = time.time()
        try:
            kwargs = {"model": self.model, "messages": messages}
            if response_format:
                kwargs["response_format"] = response_format
            response = await self.async_client.chat.completions.create(**kwargs)
            
            duration = time.time() - start_time
            performance_logger.info(f"OpenAI API call ({self.model}) completed in {duration:.2f}s")
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI Async Error: {str(e)}")
            raise e

    @openai_cb
    def _call_openai(self, messages: List[Dict[str, str]], response_format: Optional[Dict] = None) -> str:
        try:
            kwargs = {"model": self.model, "messages": messages}
            if response_format:
                kwargs["response_format"] = response_format
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI Sync Error: {str(e)}")
            raise e

    async def get_summary_async(self, content: str, max_words: int = 100) -> str:
        prompt = f"Summarize the following text in under {max_words} words.\n\nText:\n{content}\n\nSummary:"
        return await self._call_openai_async([{"role": "user", "content": prompt}])

    def get_summary(self, content: str, max_words: int = 100) -> str:
        prompt = f"Summarize the following text in under {max_words} words.\n\nText:\n{content}\n\nSummary:"
        return self._call_openai([{"role": "user", "content": prompt}])

    async def get_structured_output_async(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_str = json.dumps(json_schema, indent=2)
        prompt = f"Extract information from the following text based on the provided JSON schema.\nSchema:\n{schema_str}\n\nText:\n{content}\n\nOutput JSON:"
        messages = [{"role": "system", "content": "You are a helpful assistant that outputs JSON."}, {"role": "user", "content": prompt}]
        json_string = await self._call_openai_async(messages, response_format={"type": "json_object"})
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            logger.error(f"OpenAI failed to return valid JSON: {json_string}")
            return {}

    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_str = json.dumps(json_schema, indent=2)
        prompt = f"Extract information from the following text based on the provided JSON schema.\nSchema:\n{schema_str}\n\nText:\n{content}\n\nOutput JSON:"
        messages = [{"role": "system", "content": "You are a helpful assistant that outputs JSON."}, {"role": "user", "content": prompt}]
        json_string = self._call_openai(messages, response_format={"type": "json_object"})
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            logger.error(f"OpenAI failed to return valid JSON: {json_string}")
            return {}

    async def analyze_intent_async(self, query: str) -> str:
        prompt = f"Analyze the intent of the following user query. Respond with a short phrase.\nQuery:\n{query}\n\nIntent:"
        return (await self._call_openai_async([{"role": "user", "content": prompt}])).strip()

    def analyze_intent(self, query: str) -> str:
        prompt = f"Analyze the intent of the following user query. Respond with a short phrase.\nQuery:\n{query}\n\nIntent:"
        return self._call_openai([{"role": "user", "content": prompt}]).strip()

    async def chat_completion_async(self, message: str, context: Optional[str] = None) -> str:
        messages = []
        if context: messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": message})
        return await self._call_openai_async(messages)

    def chat_completion(self, message: str, context: Optional[str] = None) -> str:
        messages = []
        if context: messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": message})
        return self._call_openai(messages)

class OllamaService:
    def __init__(self, model: str = "llama3", base_url: str = os.getenv("LLM_API_BASE", "http://localhost:11434")):
        self.model = model
        self.base_url = base_url

    @ollama_cb
    async def _call_ollama_async(self, messages: List[Dict[str, str]], format: Optional[str] = None) -> str:
        start_time = time.time()
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}
        if format: payload["format"] = format
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=60.0)
                response.raise_for_status()
                
                duration = time.time() - start_time
                performance_logger.info(f"Ollama API call ({self.model}) completed in {duration:.2f}s")
                
                return response.json()['message']['content']
            except Exception as e:
                logger.error(f"Ollama Async Error: {str(e)}")
                raise e

    @ollama_cb
    def _call_ollama(self, messages: List[Dict[str, str]], format: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {"model": self.model, "messages": messages, "stream": False}
        if format: payload["format"] = format
        try:
            import requests
            response = requests.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            return response.json()['message']['content']
        except Exception as e:
            logger.error(f"Ollama Sync Error: {str(e)}")
            raise e

    async def get_summary_async(self, content: str, max_words: int = 100) -> str:
        prompt = f"Summarize the following text in under {max_words} words.\n\nText:\n{content}\n\nSummary:"
        return await self._call_ollama_async([{"role": "user", "content": prompt}])

    def get_summary(self, content: str, max_words: int = 100) -> str:
        prompt = f"Summarize the following text in under {max_words} words.\n\nText:\n{content}\n\nSummary:"
        return self._call_ollama([{"role": "user", "content": prompt}])

    async def get_structured_output_async(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_str = json.dumps(json_schema, indent=2)
        prompt = f"Extract information from the following text based on the provided JSON schema.\nSchema:\n{schema_str}\n\nText:\n{content}\n\nOutput JSON:"
        messages = [{"role": "system", "content": "You are a helpful assistant that outputs JSON."}, {"role": "user", "content": prompt}]
        json_string = await self._call_ollama_async(messages, format="json")
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            logger.error(f"Ollama failed to return valid JSON: {json_string}")
            return {}

    def get_structured_output(self, content: str, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        schema_str = json.dumps(json_schema, indent=2)
        prompt = f"Extract information from the following text based on the provided JSON schema.\nSchema:\n{schema_str}\n\nText:\n{content}\n\nOutput JSON:"
        messages = [{"role": "system", "content": "You are a helpful assistant that outputs JSON."}, {"role": "user", "content": prompt}]
        json_string = self._call_ollama(messages, format="json")
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            logger.error(f"Ollama failed to return valid JSON: {json_string}")
            return {}

    async def analyze_intent_async(self, query: str) -> str:
        prompt = f"Analyze the intent of the following user query. Respond with a short phrase.\nQuery:\n{query}\n\nIntent:"
        return (await self._call_ollama_async([{"role": "user", "content": prompt}])).strip()

    def analyze_intent(self, query: str) -> str:
        prompt = f"Analyze the intent of the following user query. Respond with a short phrase.\nQuery:\n{query}\n\nIntent:"
        return self._call_ollama([{"role": "user", "content": prompt}]).strip()

    async def chat_completion_async(self, message: str, context: Optional[str] = None) -> str:
        messages = []
        if context: messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": message})
        return await self._call_ollama_async(messages)

    def chat_completion(self, message: str, context: Optional[str] = None) -> str:
        messages = []
        if context: messages.append({"role": "system", "content": f"Context: {context}"})
        messages.append({"role": "user", "content": message})
        return self._call_ollama(messages)
