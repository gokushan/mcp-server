"""Base document processor."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ..config import settings
from .document_parser import DocumentParser

T = TypeVar("T", bound=BaseModel)


class BaseProcessor(ABC, Generic[T]):
    """Abstract base class for document processors."""

    def __init__(self):
        self.parser = DocumentParser()

    async def process(self, file_path: str) -> T:
        """Process a document and return structured data.

        Args:
            file_path: Path to the document

        Returns:
            Structured data model
        """
        # 1. Extract text
        text = self.parser.extract_text(file_path)

        # 2. Parse with LLM
        return await self._parse_with_llm(text)

    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get system prompt for the processor."""
        pass

    @abstractmethod
    def _get_model_class(self) -> type[T]:
        """Get the Pydantic model class for validation."""
        pass

    async def _parse_with_llm(self, text: str) -> T:
        """Parse extracted text using LLM."""
        # This is a simplified implementation. In a real scenario,
        # we would implement the specific provider logic (OpenAI, Anthropic, etc.)
        # For now, we'll mock the LLM interaction or use a simple HTTP call if keys are present.
        
        # TODO: Implement actual LLM call
        # For prototype purposes, this would call openai/anthropic API
        # passing the text and requesting JSON output matching the model schema.
        
        system_prompt = self._get_system_prompt()
        model_class = self._get_model_class()
        
        # Placeholder implementation
        # implementation detail: We would construct a prompt like:
        # "Extract the following fields from the text as JSON: {schema}"
        
        raise NotImplementedError("LLM integration to be implemented")
