"""[Port] Output Port (Interface) for Document Processing.

This module defines the interface that any document processor must implement.
It acts as a port that the application core uses to communicate with
specific document processing implementations (adapters).
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from ..config import settings
from .document_parser import DocumentParser
from ..llm.factory import get_llm_strategy

T = TypeVar("T", bound=BaseModel)


class BaseProcessor(ABC, Generic[T]):
    """Abstract base class for document processors."""

    def __init__(self):
        self.parser = DocumentParser()
        self.llm_strategy = get_llm_strategy()

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
        """Parse extracted text using LLM strategy."""
        system_prompt = self._get_system_prompt()
        model_class = self._get_model_class()
        
        # Use strategy to get JSON data
        data_dict = await self.llm_strategy.generate_json(
            system_prompt=system_prompt,
            user_content=f"Extract data from this document:\n\n{text[:settings.llm_max_chars]}"
        )
        
        # Validar con Pydantic
        return model_class(**data_dict)
