"""
Example script to test document attachment functionality.

This script demonstrates how to:
1. Create a contract with document attachment
2. Handle attachment failures
3. Retry document attachment
"""

import asyncio
from pathlib import Path

from glpi_mcp_server.glpi.api_client import GLPIAPIClient
from glpi_mcp_server.glpi.contracts import ContractManager
from glpi_mcp_server.glpi.documents import DocumentManager
from glpi_mcp_server.glpi.models import ContractData


async def example_create_contract_with_document():
    """Example: Create contract and attach document in one step."""
    
    # Initialize client
    async with GLPIAPIClient() as client:
        # Create contract
        contract_manager = ContractManager(client)
        contract_data = ContractData(
            name="Contrato de Prueba con Documento",
            num="TEST-2026-001",
            begin_date="2026-01-01",
            duration=12,
            cost=10000.00,
        )
        
        contract = await contract_manager.create(contract_data)
        print(f"✅ Contract created: ID {contract.id}")
        
        # Attach document
        doc_manager = DocumentManager(client)
        
        # Example file path - replace with actual file
        file_path = "/path/to/your/contract.pdf"
        
        try:
            document = await doc_manager.attach_to_item(
                file_path=file_path,
                item_id=contract.id,
                item_type="Contract",
                document_name=contract.name,
            )
            print(f"✅ Document attached: ID {document.id}")
            print(f"   Name: {document.name}")
            print(f"   Filename: {document.filename}")
            
        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
            print(f"   Contract created successfully (ID: {contract.id})")
            print(f"   You can retry attachment later using attach_document_to_contract tool")
        
        except Exception as e:
            print(f"❌ Attachment failed: {e}")
            print(f"   Contract created successfully (ID: {contract.id})")


async def example_retry_attachment():
    """Example: Retry document attachment for existing contract."""
    
    async with GLPIAPIClient() as client:
        doc_manager = DocumentManager(client)
        contract_manager = ContractManager(client)
        
        # Get existing contract
        contract_id = 123  # Replace with actual contract ID
        contract = await contract_manager.get(contract_id)
        
        # Retry attachment
        file_path = "/path/to/your/contract.pdf"
        
        try:
            document = await doc_manager.attach_to_item(
                file_path=file_path,
                item_id=contract_id,
                item_type="Contract",
                document_name=contract.name,
            )
            print(f"✅ Document attached successfully!")
            print(f"   Contract ID: {contract_id}")
            print(f"   Document ID: {document.id}")
            
        except Exception as e:
            print(f"❌ Retry failed: {e}")


async def example_attach_multiple_documents():
    """Example: Attach multiple documents to same contract."""
    
    async with GLPIAPIClient() as client:
        doc_manager = DocumentManager(client)
        contract_id = 123  # Replace with actual contract ID
        
        documents = [
            ("/path/to/contract_original.pdf", "Contrato Original"),
            ("/path/to/contract_signed.pdf", "Contrato Firmado"),
            ("/path/to/annex_a.pdf", "Anexo A - Especificaciones Técnicas"),
        ]
        
        for file_path, doc_name in documents:
            try:
                document = await doc_manager.attach_to_item(
                    file_path=file_path,
                    item_id=contract_id,
                    item_type="Contract",
                    document_name=doc_name,
                )
                print(f"✅ Attached: {doc_name} (ID: {document.id})")
                
            except Exception as e:
                print(f"❌ Failed to attach {doc_name}: {e}")


async def example_validate_file_before_upload():
    """Example: Validate file exists before attempting upload."""
    
    file_path = "/path/to/your/contract.pdf"
    file_obj = Path(file_path)
    
    # Validation checks
    if not file_obj.exists():
        print(f"❌ File does not exist: {file_path}")
        return
    
    if not file_obj.is_file():
        print(f"❌ Path is not a file: {file_path}")
        return
    
    if file_obj.stat().st_size == 0:
        print(f"❌ File is empty: {file_path}")
        return
    
    if file_obj.stat().st_size > 50 * 1024 * 1024:  # 50 MB
        print(f"⚠️  Warning: Large file ({file_obj.stat().st_size / 1024 / 1024:.2f} MB)")
    
    print(f"✅ File validation passed: {file_path}")
    print(f"   Size: {file_obj.stat().st_size / 1024:.2f} KB")
    print(f"   Name: {file_obj.name}")
    
    # Proceed with upload
    async with GLPIAPIClient() as client:
        doc_manager = DocumentManager(client)
        # ... upload logic


if __name__ == "__main__":
    print("=== Document Attachment Examples ===\n")
    
    # Run examples
    # asyncio.run(example_create_contract_with_document())
    # asyncio.run(example_retry_attachment())
    # asyncio.run(example_attach_multiple_documents())
    # asyncio.run(example_validate_file_before_upload())
    
    print("\nUncomment the example you want to run!")
