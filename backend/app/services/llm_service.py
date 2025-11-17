"""
LLM Service
Handles integration with Ollama for text generation and chat completion
"""

import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp
from loguru import logger

from app.core.config import get_settings

settings = get_settings()


class LLMService:
    """
    Service for interacting with Ollama LLM
    Provides text generation, chat completion, and streaming capabilities
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes for LLM responses

    async def _make_request(
        self, endpoint: str, payload: Dict[str, Any], stream: bool = False
    ) -> Any:
        """
        Make HTTP request to Ollama API

        Args:
            endpoint: API endpoint
            payload: Request payload
            stream: Whether to stream the response

        Returns:
            Response data or async generator for streaming

        Raises:
            Exception: If request fails
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {error_text}")
                        raise Exception(f"Ollama API error: {response.status}")

                    if stream:
                        return self._stream_response(response)
                    else:
                        return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {str(e)}")
            raise Exception(f"Failed to connect to Ollama: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in LLM request: {str(e)}")
            raise

    async def _stream_response(
        self, response: aiohttp.ClientResponse
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from Ollama

        Args:
            response: HTTP response object

        Yields:
            Streamed text chunks
        """
        try:
            async for line in response.content:
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        if "response" in data:
                            yield data["response"]
                        elif "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logger.error(f"Error streaming response: {str(e)}")
            raise

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """
        Generate text from prompt using Ollama

        Args:
            prompt: User prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system prompt
            stream: Whether to stream the response

        Returns:
            Generated text or async generator if streaming

        Example:
            # Non-streaming
            response = await llm_service.generate("What is banking?")

            # Streaming
            async for chunk in await llm_service.generate("Explain loans", stream=True):
                print(chunk, end='')
        """
        logger.info(f"Generating text with model: {self.model}")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        if system_prompt:
            payload["system"] = system_prompt

        try:
            if stream:
                response = await self._make_request(
                    "api/generate", payload, stream=True
                )
                return response
            else:
                response = await self._make_request(
                    "api/generate", payload, stream=False
                )
                return response.get("response", "")

        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
    ) -> str | AsyncGenerator[str, None]:
        """
        Chat completion with conversation history

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Generated response or async generator if streaming

        Example:
            messages = [
                {"role": "system", "content": "You are a banking assistant"},
                {"role": "user", "content": "What is a savings account?"},
                {"role": "assistant", "content": "A savings account is..."},
                {"role": "user", "content": "What about checking accounts?"}
            ]
            response = await llm_service.chat(messages)
        """
        logger.info(f"Chat completion with {len(messages)} messages")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            },
        }

        if max_tokens:
            payload["options"]["num_predict"] = max_tokens

        try:
            if stream:
                response = await self._make_request("api/chat", payload, stream=True)
                return response
            else:
                response = await self._make_request("api/chat", payload, stream=False)
                return response.get("message", {}).get("content", "")

        except Exception as e:
            logger.error(f"Chat completion failed: {str(e)}")
            raise

    async def stream(
        self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Stream text generation (convenience method)

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature

        Yields:
            Text chunks as they're generated

        Example:
            async for chunk in llm_service.stream("Tell me about banking"):
                print(chunk, end='', flush=True)
        """
        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            stream=True,
        )

        async for chunk in response:
            yield chunk

    async def chat_stream(
        self, messages: List[Dict[str, str]], temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion (convenience method)

        Args:
            messages: Conversation history
            temperature: Sampling temperature

        Yields:
            Text chunks as they're generated

        Example:
            messages = [{"role": "user", "content": "Hello"}]
            async for chunk in llm_service.chat_stream(messages):
                print(chunk, end='', flush=True)
        """
        response = await self.chat(
            messages=messages, temperature=temperature, stream=True
        )

        async for chunk in response:
            yield chunk

    async def check_health(self) -> bool:
        """
        Check if Ollama service is available

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = [model["name"] for model in data.get("models", [])]
                        logger.info(f"Ollama is healthy. Available models: {models}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"Ollama health check failed: {str(e)}")
            return False

    async def list_models(self) -> List[str]:
        """
        List available models in Ollama

        Returns:
            List of model names

        Example:
            models = await llm_service.list_models()
            print(f"Available models: {models}")
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        return [model["name"] for model in data.get("models", [])]
                    return []
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []

    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama registry

        Args:
            model_name: Name of the model to pull

        Returns:
            True if successful, False otherwise

        Example:
            success = await llm_service.pull_model("llama3.1:latest")
        """
        try:
            logger.info(f"Pulling model: {model_name}")

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=3600)
            ) as session:
                async with session.post(
                    f"{self.base_url}/api/pull", json={"name": model_name}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Successfully pulled model: {model_name}")
                        return True
                    return False
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {str(e)}")
            return False

    async def get_embeddings(self, text: str) -> List[float]:
        """
        Get embeddings for text using Ollama

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Note:
            This uses Ollama's embedding endpoint.
            For dedicated embedding service, use EmbeddingService instead.
        """
        try:
            payload = {"model": self.model, "prompt": text}

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.base_url}/api/embeddings", json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("embedding", [])
                    return []
        except Exception as e:
            logger.error(f"Failed to get embeddings: {str(e)}")
            return []


# Global instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get singleton instance of LLM service

    Returns:
        LLMService instance
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
