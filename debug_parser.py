
import sys
from glpi_mcp_server.config import settings
from glpi_mcp_server.processors.document_parser import DocumentParser

print(f"Allowed extensions: {settings.allowed_extensions_list}")
file_path = "/home/gokushan/Documentos/batch/ollama_contrato.txt"

print(f"Attempting to read: {file_path}")

try:
    # First check if path exists
    from pathlib import Path
    p = Path(file_path)
    if not p.exists():
        print(f"File does not exist: {file_path}")
    else:
        print(f"File exists. Size: {p.stat().st_size} bytes")

    text = DocumentParser.extract_text(file_path)
    print("Successfully read text.")
    print(f"Length: {len(text)}")
except Exception as e:
    print(f"Error reading file: {e}")
    import traceback
    traceback.print_exc()
