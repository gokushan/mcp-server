import asyncio
import logging
import sys
from glpi_mcp_server.processors.contract_processor import ContractProcessor
from glpi_mcp_server.config import settings

# Configure basic logging for the script itself to confuse with the processor's output if needed, 
# but mostly we want to see the processor's output on stderr.
logging.basicConfig(level=logging.INFO)

async def main():
    print("Initiating test...", file=sys.stderr)
    processor = ContractProcessor()
    
    # We'll just call the method with short text. 
    # This will likely fail due to missing API keys or network if not configured, 
    # but we should see the initial log message "Start _parse_with_llm..." before any crash.
    try:
        print("Calling _parse_with_llm...", file=sys.stderr)
        await processor._parse_with_llm("Test contract content for logging verification.")
    except Exception as e:
        print(f"caught expected exception (likely API related): {e}", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())
