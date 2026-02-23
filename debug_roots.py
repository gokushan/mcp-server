
import sys
from pathlib import Path
from glpi_mcp_server.config import settings
from glpi_mcp_server.tools.utils import is_path_allowed

print("--- Debugging Configuration ---")
try:
    roots = settings.allowed_roots_list
    print(f"Allowed roots ({len(roots)}):")
    for r in roots:
        print(f"  - {r} (Exists: {r.exists()})")
except Exception as e:
    print(f"Error loading roots: {e}")

file_path = "/home/gokushan/Documentos/batch/ollama_contrato.txt"
print(f"\n--- Checking Path: {file_path} ---")

try:
    allowed = is_path_allowed(file_path)
    print(f"is_path_allowed('{file_path}') = {allowed}")
except Exception as e:
    print(f"Error in is_path_allowed: {e}")

if not allowed:
    print("WARNING: Path is NOT allowed.")
else:
    print("Path is allowed.")

