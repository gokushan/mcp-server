from pathlib import Path
import sys
sys.path.append(str(Path.cwd() / "src"))
from glpi_mcp_server.processors.document_parser import DocumentParser

test_file = Path("/home/gokushan/Documentos/Contrato_Narrativo_CONT-2026-IT-0087.pdf")
text = DocumentParser.extract_text(test_file)
print(text)
