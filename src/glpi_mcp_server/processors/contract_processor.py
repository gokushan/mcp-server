"""[Adapter] Secondary Adapter (Driven) for Contract Processing.

This module implements the specific logic for processing Contract documents,
acting as a driven adapter that uses an LLM to parse content.
"""

import json

from ..config import settings
from ..glpi.models import ProcessedContract
from .base_processor import BaseProcessor


class ContractProcessor(BaseProcessor[ProcessedContract]):
    """Processor for contract documents."""

    def _get_model_class(self) -> type[ProcessedContract]:
        return ProcessedContract

    def _get_system_prompt(self) -> str:
        return """You are an expert legal AI assistant. Your task is to extract structured data from the provided contract text.
        
Extract the following information:
- Contract name
- Contract number/reference (contract_num)
- Accounting number/reference (accounting_number)
- Parties involved (Client and Provider)
- Start and End dates (YYYY-MM-DD format)
- Duration in months (duration_months) - Calculate if not explicitly stated but start/end dates are present.
- Notice period in months (notice_months) needed for termination/non-renewal.
- Renewal type (renewal_type): "automatic", "manual", "none".
- Renewal Enum (renewal_enum): 1 for Automatic/Tacit, 2 for Express/Manual/None.
- Billing/Payment frequency in months (billing_frequency_months). E.g., Monthly=1, Quarterly=3, Yearly=12.
- Contract amount/cost
- Currency
- Payment terms
- SLA/Support Hours (sla_support_hours): Extract as a dictionary if mentioned (e.g., {"week_days": "Mon-Fri", "hours": "9-17", "response_time": "..."}).
- Key terms (list of important clauses)
- Brief summary of the contract

Return the output as a valid JSON object matching the requested schema. Do not include any explanation, only the JSON."""

    async def _parse_with_llm(self, text: str) -> ProcessedContract:
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
                            {"role": "user", "content": f"Extract data from this contract:\n\n{text[:20000]}"}
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
                return ProcessedContract(**data)

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
                            {"role": "user", "content": f"Extract data from this contract:\n\n{text[:10000]}"}
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
                return ProcessedContract(**data)
        
        else:
            raise ValueError(f"Unsupported LLM Provider: {settings.llm_provider}")
