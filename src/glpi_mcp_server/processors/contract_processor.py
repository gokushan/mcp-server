"""Contract document processor."""

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
- Parties involved (Client and Provider)
- Start and End dates (YYYY-MM-DD format)
- Renewal type (automatic, manual, none)
- Contract amount/cost
- Currency
- Payment terms
- Key terms (list of important clauses)
- Brief summary of the contract

Return the output as a valid JSON object matching the requested schema. Do not include any explanation, only the JSON."""

    async def _parse_with_llm(self, text: str) -> ProcessedContract:
        # Simple OpenAI implementation for prototype
        if settings.llm_provider != "openai":
            # For now only OpenAI is implemented in this snippet
            # In real filtering we would switch based on provider
            pass

        import httpx

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
                        {"role": "user", "content": f"Extract data from this contract:\n\n{text[:10000]}"} # Truncate for safety
                    ],
                    "response_format": {"type": "json_object"}
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"LLM API Error: {response.text}")
                
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            data = json.loads(content)
            
            return ProcessedContract(**data)
