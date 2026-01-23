"""[Adapter] Secondary Adapter (Driven) for Invoice Processing.

This module implements the specific logic for processing Invoice documents,
acting as a driven adapter that uses an LLM to parse content.
"""

import json

from ..config import settings
from ..glpi.models import ProcessedInvoice
from .base_processor import BaseProcessor


class InvoiceProcessor(BaseProcessor[ProcessedInvoice]):
    """Processor for invoice documents."""

    def _get_model_class(self) -> type[ProcessedInvoice]:
        return ProcessedInvoice

    def _get_system_prompt(self) -> str:
        return """You are an expert financial AI assistant. Your task is to extract structured data from the provided invoice text.
        
Extract the following information:
- Invoice number
- Vendor name
- Client name
- Invoice date (YYYY-MM-DD)
- Due date (YYYY-MM-DD)
- Line items (description, quantity, unit_price, total)
- Subtotal
- Tax amount
- Total amount
- Currency
- Payment method
- Bank account details if available

Return the output as a valid JSON object matching the requested schema. Do not include any explanation, only the JSON."""

    async def _parse_with_llm(self, text: str) -> ProcessedInvoice:
        import httpx

        if settings.llm_provider == "anthropic":
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
                        "system": self._get_system_prompt(),
                        "messages": [
                            {"role": "user", "content": f"Extract data from this invoice:\n\n{text[:20000]}"}
                        ],
                    },
                    timeout=60.0
                )

                if response.status_code != 200:
                    raise ValueError(f"Anthropic API Error: {response.text}")

                result = response.json()
                content = result["content"][0]["text"]
                # Clean up json markdown if present
                content = content.replace("```json", "").replace("```", "").strip()
                data = json.loads(content)
                return ProcessedInvoice(**data)

        elif settings.llm_provider == "openai":
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": settings.openai_model,
                        "messages": [
                            {"role": "system", "content": self._get_system_prompt()},
                            {"role": "user", "content": f"Extract data from this invoice:\n\n{text[:10000]}"}
                        ],
                        "response_format": {"type": "json_object"}
                    },
                    timeout=60.0
                )
                
                if response.status_code != 200:
                    raise ValueError(f"OpenAI API Error: {response.text}")
                    
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                data = json.loads(content)
                return ProcessedInvoice(**data)
        
        else:
            raise ValueError(f"Unsupported LLM Provider: {settings.llm_provider}")
