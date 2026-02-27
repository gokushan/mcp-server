import json
import logging
from abc import ABC, abstractmethod
from typing import Any
import httpx
from ..config import settings

logger = logging.getLogger(__name__)


class LLMCancelledError(RuntimeError):
    """Raised when an LLM call is cancelled or times out (e.g. MCP session disconnect)."""
    pass


class LLMStrategy(ABC):
    """Abstract base class for LLM provider strategies."""

    @abstractmethod
    async def generate_json(self, system_prompt: str, user_content: str, timeout: float | None = None) -> dict[str, Any]:
        """Generate structured JSON from LLM."""
        pass

    @abstractmethod
    async def generate_text(self, system_prompt: str, user_content: str, timeout: float | None = None) -> str:
        """Generate plain text from LLM."""
        pass

    def _clean_json_content(self, content: str) -> str:
        """Remove markdown code blocks from JSON content."""
        return content.replace("```json", "").replace("```", "").strip()

class OpenAIStrategy(LLMStrategy):
    """OpenAI implementation of LLM Strategy."""

    async def generate_json(self, system_prompt: str, user_content: str, timeout: float | None = None) -> dict[str, Any]:
        logger.info("OpenAI Request - System: %s", system_prompt)
        logger.info("OpenAI Request - User Content: %s", user_content)
        
        request_timeout = timeout if timeout is not None else settings.timeout_llm
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.openai_url,
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    "response_format": {"type": "json_object"}
                },
                timeout=request_timeout
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API Error: {response.text}")
                raise ValueError(f"OpenAI API Error: {response.status_code}")
                
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return json.loads(self._clean_json_content(content))

    async def generate_text(self, system_prompt: str, user_content: str, timeout: float | None = None) -> str:
        logger.info("OpenAI Request (Text) - System: %s", system_prompt)
        logger.info("OpenAI Request (Text) - User Content: %s", user_content)
        
        request_timeout = timeout if timeout is not None else settings.timeout_llm
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.openai_url,
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ]
                },
                timeout=request_timeout
            )
            if response.status_code != 200:
                logger.error(f"OpenAI API Error: {response.text}")
                raise ValueError(f"OpenAI API Error: {response.status_code}")
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()

class AnthropicStrategy(LLMStrategy):
    """Anthropic implementation of LLM Strategy."""

    async def generate_json(self, system_prompt: str, user_content: str, timeout: float | None = None) -> dict[str, Any]:
        logger.info("Anthropic Request - System: %s", system_prompt)
        logger.info("Anthropic Request - User Content: %s", user_content)
        
        request_timeout = timeout if timeout is not None else settings.timeout_llm
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.anthropic_base_url}/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_content}
                    ],
                },
                timeout=request_timeout
            )

            if response.status_code != 200:
                logger.error(f"Anthropic API Error: {response.text}")
                raise ValueError(f"Anthropic API Error: {response.status_code}")

            result = response.json()
            content = result["content"][0]["text"]
            return json.loads(self._clean_json_content(content))

    async def generate_text(self, system_prompt: str, user_content: str, timeout: float | None = None) -> str:
        logger.info("Anthropic Request (Text) - System: %s", system_prompt)
        logger.info("Anthropic Request (Text) - User Content: %s", user_content)
        
        request_timeout = timeout if timeout is not None else settings.timeout_llm
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.anthropic_base_url}/messages",
                headers={
                    "x-api-key": settings.anthropic_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.anthropic_model,
                    "max_tokens": 4096,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": user_content}
                    ],
                },
                timeout=request_timeout
            )
            if response.status_code != 200:
                logger.error(f"Anthropic API Error: {response.text}")
                raise ValueError(f"Anthropic API Error: {response.status_code}")
            result = response.json()
            return result["content"][0]["text"].strip()

class OllamaStrategy(LLMStrategy):
    """Ollama implementation of LLM Strategy."""

    async def generate_json(self, system_prompt: str, user_content: str, timeout: float | None = None) -> dict[str, Any]:
        url = f"{settings.ollama_base_url}/api/chat"
        model = settings.ollama_model
        request_timeout = timeout if timeout is not None else settings.timeout_llm
        logger.info("[Ollama/JSON] Calling %s | model=%s | timeout=%ss", url, model, request_timeout)
        logger.debug("[Ollama/JSON] system_prompt=%s", system_prompt[:300])
        logger.debug("[Ollama/JSON] user_content (first 500 chars)=%s", user_content[:500])
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "stream": False,
                        "format": "json"
                    },
                    timeout=request_timeout
                )

                logger.info("[Ollama/JSON] HTTP status: %s", response.status_code)

                if response.status_code != 200:
                    logger.error("[Ollama/JSON] Error response body: %s", response.text)
                    raise ValueError(f"Ollama API Error: {response.status_code}")

                result = response.json()
                content = result["message"]["content"]
                logger.debug("[Ollama/JSON] Raw content from Ollama: %s", content)

                try:
                    parsed = json.loads(self._clean_json_content(content))
                    logger.info("[Ollama/JSON] JSON parsed successfully. Keys: %s", list(parsed.keys()))
                    return parsed
                except json.JSONDecodeError as json_err:
                    logger.error("[Ollama/JSON] JSON parsing FAILED. Error: %s | Raw content: %s", json_err, content)
                    raise
        except httpx.TimeoutException as te:
            logger.error("[Ollama/JSON] Request TIMED OUT after %ss. Error: %s", request_timeout, te)
            raise LLMCancelledError(f"Ollama request timed out after {request_timeout}s") from te
        except httpx.ConnectError as ce:
            logger.error("[Ollama/JSON] Connection ERROR to %s. Is Ollama running? Error: %s", url, ce)
            raise
        except BaseException as be:
            # CancelledError (anyio/asyncio) is a BaseException, not Exception.
            # It is raised when the MCP session loop cancels the task (e.g. client disconnects).
            logger.error(
                "[Ollama/JSON] Task CANCELLED while waiting for Ollama response "
                "(likely MCP session timeout/disconnect). type=%s | error=%s",
                type(be).__name__, be
            )
            raise LLMCancelledError(f"Ollama call cancelled by MCP session ({type(be).__name__})") from be

    async def generate_text(self, system_prompt: str, user_content: str, timeout: float | None = None) -> str:
        url = f"{settings.ollama_base_url}/api/chat"
        model = settings.ollama_model
        request_timeout = timeout if timeout is not None else settings.timeout_llm
        logger.info("[Ollama/Text] Calling %s | model=%s | timeout=%ss", url, model, request_timeout)
        logger.debug("[Ollama/Text] system_prompt=%s", system_prompt[:300])
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        "stream": False
                    },
                    timeout=request_timeout
                )
                logger.info("[Ollama/Text] HTTP status: %s", response.status_code)
                if response.status_code != 200:
                    logger.error("[Ollama/Text] Error response body: %s", response.text)
                    raise ValueError(f"Ollama API Error: {response.status_code}")
                result = response.json()
                content = result["message"]["content"].strip()
                logger.info("[Ollama/Text] Response received. Length: %d chars", len(content))
                logger.debug("[Ollama/Text] Raw content: %s", content[:500])
                return content
        except httpx.TimeoutException as te:
            logger.error("[Ollama/Text] Request TIMED OUT after %ss. Error: %s", request_timeout, te)
            raise LLMCancelledError(f"Ollama request timed out after {request_timeout}s") from te
        except httpx.ConnectError as ce:
            logger.error("[Ollama/Text] Connection ERROR to %s. Is Ollama running? Error: %s", url, ce)
            raise
        except BaseException as be:
            # CancelledError (anyio/asyncio) is a BaseException, not Exception.
            # It is raised when the MCP session loop cancels the task (e.g. client disconnects).
            logger.error(
                "[Ollama/Text] Task CANCELLED while waiting for Ollama response "
                "(likely MCP session timeout/disconnect). type=%s | error=%s",
                type(be).__name__, be
            )
            raise LLMCancelledError(f"Ollama call cancelled by MCP session ({type(be).__name__})") from be


class MockStrategy(LLMStrategy):
    """Mock implementation of LLM Strategy for faster development."""

    async def generate_json(self, system_prompt: str, user_content: str, timeout: float | None = None) -> dict[str, Any]:
        logger.info("MOCK LLM Request (JSON)")
        
        # Simulate prompt injection if the keyword is present
        is_malicious = "INJECTION_TEST" in user_content or "INJECTION_TEST" in system_prompt
        
        # Mock data for a contract
        return {
            "contract_name": "Contrato de Mantenimiento de Prueba",
            "is_contract": True,
            "contract_type": "Mantenimiento",
            "parties": {
                "client": {"name": "Cliente de Prueba S.A.", "id": "B12345678", "address": "Calle Falsa 123"},
                "provider": {"name": "Proveedor Mock S.L.", "id": "B87654321", "address": "Avenida Siempre Viva 742"}
            },
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "duration_months": 12,
            "renewal_enum": 1,
            "notice_months": 2,
            "billing_frequency_months": 3,
            "amount": 5000.00,
            "currency": "EUR",
            "payment_terms": "Transferencia 30 días",
            "sla_support_hours": {
                "week_begin_hour": "08:00:00",
                "week_end_hour": "18:00:00",
                "use_saturday": 0,
                "saturday_begin_hour": "00:00:00",
                "saturday_end_hour": "00:00:00",
                "use_sunday": 0,
                "sunday_begin_hour": "00:00:00",
                "sunday_end_hour": "00:00:00"
            },
            "key_terms": ["Mock", "Prueba", "Desarrollo"],
            "summary": "Este es un contrato generado por el Mock LLM para propósitos de desarrollo.",
            "prompt_injection_detected": is_malicious
        }

    async def generate_text(self, system_prompt: str, user_content: str, timeout: float | None = None) -> str:
        logger.info("MOCK LLM Request (Text)")
        if "procesado un lote de contratos" in system_prompt:
             return "Estimado usuario/a:\n\nEl procesamiento del lote se ha completado correctamente (MOCK). Los contratos han sido creados en GLPI y los archivos movidos a sus carpetas correspondientes."
        return "Respuesta simulada del LLM (MOCK)."
