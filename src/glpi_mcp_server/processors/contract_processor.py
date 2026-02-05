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
- Contract name (name)
- Contract number/reference (num)
- Accounting number/reference (accounting_number)
- Parties involved (parties): A dictionary with "client" and "provider" keys, each containing "name", "id", and "address".
- Start date (begin_date) and End date (end_date) in YYYY-MM-DD format.
- Duration in months (duration): Calculate if only dates are provided.
- Notice period in months (notice) for termination.
- Renewal Enum (renewal): 1 for Automatic/Tacit, 2 for Express/Manual/None.
- Billing frequency in months (billing).
- Total contract amount (cost): A float number.
- Currency (currency): E.g., "EUR".
- Payment terms (payment_terms)
- SLA/Support Hours (sla_support_hours): A dictionary with keys: week_begin_hour, week_end_hour, use_saturday, saturday_begin_hour, saturday_end_hour, use_sunday, sunday_begin_hour, sunday_end_hour.
- Key terms (key_terms): List of important clauses.
- Summary (comment): A concise overview.

Return valid JSON matching the schema. Numeric fields should be numbers, not strings. Do not include markdown tags. """

    async def _parse_with_llm(self, text: str) -> ProcessedContract:
        # MOCK: Provisión temporal para evitar gastos de API
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("USANDO DATOS MOCKEADOS PARA EL PROCESAMIENTO DEL CONTRATO")
        
        dummy_data = {
            "name": "CONTRATO DE SERVICIOS MANTENIMIENTO MOCK",
            "num": "MOCK-2024-001",
            "accounting_number": "ACCT-9999",
            "parties": {
                "client": {"name": "Empresa Cliente S.A.", "id": "B12345678", "address": "Calle Falsa 123, Madrid"},
                "provider": {"name": "Servicios Tech S.L.", "id": "B87654321", "address": "Avenida de la Tecnología 45, Barcelona"}
            },
            "begin_date": "2024-01-01",
            "end_date": "2024-12-31",
            "duration": 12,
            "renewal": 1,
            "notice": 2,
            "billing": 3,
            "cost": 12500.50,
            "currency": "EUR",
            "payment_terms": "30 días después de factura",
            "sla_support_hours": {
                "week_begin_hour": "08:00:00",
                "week_end_hour": "18:00:00",
                "use_saturday": 1,
                "saturday_begin_hour": "09:00:00",
                "saturday_end_hour": "14:00:00",
                "use_sunday": 0
            },
            "key_terms": ["Confidencialidad", "Nivel de servicio 99.9%", "Propiedad intelectual"],
            "comment": "Contrato de mantenimiento preventivo y correctivo de sistemas informáticos (DATOS DE PRUEBA)."
        }
        return ProcessedContract(**dummy_data)

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
                        "max_tokens": 1024,
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
