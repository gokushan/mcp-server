"""Low-level document parsing utilities."""

from pathlib import Path

import pdfplumber
from docx import Document

from ..config import settings
from ..tools.error_codes import FileExtensionError, FileReadError


class DocumentParser:
    """Parser for extracting text from documents."""

    @staticmethod
    def extract_text(file_path: str | Path) -> str:
        """Extract text from file based on extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text

        Raises:
            FileNotFoundError: If the file does not exist.
            FileExtensionError: If the file extension is not allowed.
            FileReadError: If the file cannot be read or is malformed.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Validate extension against allowed list
        ext = file_path.suffix.lower().lstrip(".")
        if ext not in settings.allowed_extensions_list:
            raise FileExtensionError(
                f"File extension '{ext}' is not allowed. Allowed: {settings.allowed_extensions_list}"
            )
            
        if file_path.suffix.lower() == ".pdf":
            return DocumentParser._extract_from_pdf(file_path)
        elif file_path.suffix.lower() in [".docx", ".doc"]:
            return DocumentParser._extract_from_docx(file_path)
        elif file_path.suffix.lower() == ".txt":
            try:
                return file_path.read_text(encoding="utf-8")
            except Exception as e:
                raise FileReadError(f"Cannot read text file '{file_path}': {e}") from e
        else:
            raise FileExtensionError(f"Unsupported file type: {file_path.suffix}")

    @staticmethod
    def _extract_from_pdf(file_path: Path) -> str:
        try:
            text = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text.append(extracted)
            return "\n\n".join(text)
        except Exception as e:
            raise FileReadError(f"Cannot read PDF file '{file_path}': {e}") from e

    @staticmethod
    def _extract_from_docx(file_path: Path) -> str:
        try:
            doc = Document(file_path)
            text = [paragraph.text for paragraph in doc.paragraphs if paragraph.text]
            return "\n\n".join(text)
        except Exception as e:
            raise FileReadError(f"Cannot read DOCX file '{file_path}': {e}") from e
