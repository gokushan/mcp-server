"""[Adapter] Secondary Adapter (Driven) for Invoice Processing.

This module implements the specific logic for processing Invoice documents,
acting as a driven adapter that uses an LLM to parse content.
"""


from ..config import settings
from ..glpi.models import ProcessedInvoice
from .base_processor import BaseProcessor
from .utils import normalize_date


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
        """Override to add custom normalization logic after generic parsing."""
        invoice = await super()._parse_with_llm(text)
        
        # Post-processing normalization
        invoice.begin_date = normalize_date(invoice.begin_date)
        invoice.end_date = normalize_date(invoice.end_date)
        
        return invoice
