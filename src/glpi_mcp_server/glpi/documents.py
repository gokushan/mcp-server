"""Document management operations."""

import logging
from pathlib import Path
from typing import Any

from .api_client import GLPIAPIClient
from .models import DocumentData, DocumentResponse

logger = logging.getLogger(__name__)


class DocumentManager:
    """Manager for GLPI documents.
    
    This class handles document uploads and attachments to GLPI items
    following the Single Responsibility Principle.
    """

    def __init__(self, client: GLPIAPIClient):
        """Initialize document manager.
        
        Args:
            client: GLPI API client instance
        """
        self.client = client
        self.endpoint = "Document"

    async def attach_to_item(
        self,
        file_path: str,
        item_id: int,
        item_type: str,
        document_name: str | None = None,
        comment: str | None = None,
    ) -> DocumentResponse:
        """Attach a document to a GLPI item (Contract, Ticket, etc.).

        Args:
            file_path: Absolute path to the file to upload
            item_id: ID of the item to attach to (e.g., contract ID)
            item_type: Type of item (e.g., "Contract", "Ticket")
            document_name: Optional name for the document (defaults to contract name)
            comment: Optional comment

        Returns:
            Created document details

        Raises:
            FileNotFoundError: If file doesn't exist or is not accessible
            ValueError: If file path is invalid
            httpx.HTTPError: If upload fails
        """
        # Validate file exists and is accessible
        file_obj = Path(file_path)
        if not file_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_obj.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        # Use filename as document name if not provided
        filename = file_obj.name
        doc_name = document_name or filename

        # Build upload manifest according to GLPI API spec
        manifest = {
            "input": {
                "name": doc_name,
                "_filename": [filename],
                "items_id": item_id,
                "itemtype": item_type,
            }
        }

        if comment:
            manifest["input"]["comment"] = comment

        logger.info(
            f"Uploading document '{doc_name}' to {item_type} ID {item_id}"
        )

        # Upload file using multipart/form-data
        response = await self.client.upload_file(
            endpoint=self.endpoint,
            file_path=str(file_obj.absolute()),
            manifest=manifest,
        )

        # Extract document ID from response
        if isinstance(response, list) and len(response) > 0:
            doc_id = response[0].get("id")
        elif isinstance(response, dict):
            doc_id = response.get("id")
        else:
            raise ValueError(f"Unexpected response format: {response}")

        if not doc_id:
            raise ValueError(f"No document ID in response: {response}")

        logger.info(f"Document uploaded successfully with ID {doc_id}")

        # Return document details
        return DocumentResponse(
            id=doc_id,
            name=doc_name,
            filename=filename,
            items_id=item_id,
            itemtype=item_type,
        )

    async def get(self, document_id: int) -> DocumentResponse:
        """Get document details.

        Args:
            document_id: Document ID

        Returns:
            Document details
        """
        data = await self.client.get(f"{self.endpoint}/{document_id}")

        return DocumentResponse(
            id=data.get("id"),
            name=data.get("name"),
            filename=data.get("filename"),
            upload_file=data.get("upload_file"),
            date_creation=data.get("date_creation"),
            date_mod=data.get("date_mod"),
            items_id=data.get("items_id"),
            itemtype=data.get("itemtype"),
        )

    async def delete(self, document_id: int) -> bool:
        """Delete a document.

        Args:
            document_id: Document ID

        Returns:
            True if successful
        """
        return await self.client.delete(f"{self.endpoint}/{document_id}")

    async def list_for_item(self, item_id: int, itemtype: str) -> list[DocumentResponse]:
        """List documents associated with a specific GLPI item.

        Args:
            item_id: ID of the item
            itemtype: Type of item (e.g., "Contract")

        Returns:
            List of documents
        """
        # In GLPI, listing documents for an item is done via the itemtype/:id/Document_Item endpoint
        endpoint = f"{itemtype}/{item_id}/Document_Item"
        try:
            raw_list = await self.client.get(endpoint)
        except Exception as e:
            logger.error(f"Failed to list documents for {itemtype} {item_id}: {str(e)}")
            return []
        
        if not isinstance(raw_list, list):
            raw_list = [raw_list] if raw_list else []
            
        documents = []
        for link in raw_list:
            doc_id = link.get("documents_id")
            if doc_id:
                try:
                    # Get the actual document details
                    doc_data = await self.get(doc_id)
                    documents.append(doc_data)
                except Exception:
                    # If we can't get one document, we still try others
                    continue
            
        return documents
