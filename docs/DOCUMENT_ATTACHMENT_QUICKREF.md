# Document Attachment Feature - Quick Reference

## 🎯 What Changed?

### New Files
```
server/src/glpi_mcp_server/glpi/
└── documents.py                    # NEW: DocumentManager domain service

server/docs/
└── DOCUMENT_ATTACHMENT.md          # NEW: Feature documentation

server/examples/
└── document_attachment_example.py  # NEW: Usage examples
```

### Modified Files
```
server/src/glpi_mcp_server/glpi/
├── models.py                       # Added: DocumentData, DocumentResponse
├── api_client.py                   # Added: upload_file() method
└── server.py                       # Modified: create_glpi_contract
                                    # Added: attach_document_to_contract tool
```

## 🚀 Quick Start

### Option 1: Create Contract with Document (Automatic)
```python
# Via MCP Tool
result = create_glpi_contract(
    name="Contrato ACME 2026",
    begin_date="2026-01-01",
    cost=50000.00,
    file_path="/path/to/contract.pdf"  # ← NEW PARAMETER
)

# Response includes document info:
# {
#   "id": 123,
#   "name": "Contrato ACME 2026",
#   "document_attached": true,      # ← NEW
#   "document_id": 456,             # ← NEW
#   "document_name": "Contrato ACME 2026"  # ← NEW
# }
```

### Option 2: Attach Document Later (Manual Retry)
```python
# Via NEW MCP Tool
result = attach_document_to_contract(
    contract_id=123,
    file_path="/path/to/contract.pdf"
)

# Response:
# {
#   "success": true,
#   "contract_id": 123,
#   "document_id": 456,
#   "message": "Document attached successfully..."
# }
```

## 📋 MCP Tools Available

### Modified Tool: `create_glpi_contract`
**New Parameter:**
- `file_path` (optional): Path to contract document

**New Response Fields:**
- `document_attached`: Boolean indicating if document was attached
- `document_id`: ID of attached document (if successful)
- `document_name`: Name of attached document (if successful)
- `document_error`: Error message (if attachment failed)
- `warning`: User-friendly warning with retry instructions (if failed)

### New Tool: `attach_document_to_contract`
**Parameters:**
- `contract_id` (required): Contract ID to attach to
- `file_path` (required): Absolute path to document
- `document_name` (optional): Custom document name

**Returns:**
- `success`: Boolean
- `contract_id`: Contract ID
- `document_id`: Created document ID
- `document_name`: Document name in GLPI
- `filename`: Original filename
- `message`: Success message

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MCP Tools Layer                      │
│  (server.py)                                            │
│  - create_glpi_contract(file_path?)                    │
│  - attach_document_to_contract()                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Domain Services Layer                   │
│  - ContractManager (contracts.py)                      │
│  - DocumentManager (documents.py)  ← NEW               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Infrastructure Layer                       │
│  - GLPIAPIClient (api_client.py)                       │
│    - post()                                             │
│    - upload_file()  ← NEW                              │
└─────────────────────────────────────────────────────────┘
```

## ✅ SOLID Principles Applied

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | DocumentManager only handles documents |
| **Open/Closed** | Extended without modifying ContractManager |
| **Liskov Substitution** | All managers use same GLPIAPIClient interface |
| **Interface Segregation** | Separate methods for different operations |
| **Dependency Inversion** | Managers depend on GLPIAPIClient abstraction |

## 🔍 Error Handling

### Scenario 1: File Not Found
```python
# Contract created: ✅
# Document attached: ❌
# Response includes:
{
  "id": 123,
  "document_attached": false,
  "document_error": "File not found: /path/to/file.pdf",
  "warning": "Contract created successfully (ID: 123), but document attachment failed: File not found. You can retry using 'attach_document_to_contract' tool."
}
```

### Scenario 2: GLPI Upload Error
```python
# Contract created: ✅
# Document attached: ❌
# Response includes warning with retry instructions
```

### Scenario 3: Success
```python
# Contract created: ✅
# Document attached: ✅
{
  "id": 123,
  "document_attached": true,
  "document_id": 456,
  "document_name": "Contrato ACME 2026"
}
```

## 🧪 Testing

### Test in MCP Inspector
1. Start inspector: `npx @modelcontextprotocol/inspector python3 -m glpi_mcp_server.server`
2. Navigate to "Tools" tab
3. Find `create_glpi_contract` tool
4. Fill in required fields + `file_path`
5. Execute and verify response

### Test Standalone Attachment
1. Create contract without document first
2. Use `attach_document_to_contract` tool
3. Provide contract ID and file path
4. Verify document appears in GLPI

## 📝 GLPI API Format

### Upload Request
```bash
curl -X POST "http://glpi/apirest.php/Document/" \
  -H "App-Token: xxx" \
  -H "Session-Token: xxx" \
  -F 'uploadManifest={"input":{"name":"Doc Name","_filename":["file.pdf"],"items_id":123,"itemtype":"Contract"}}' \
  -F 'filename[]=@/path/to/file.pdf'
```

### Response
```json
[
  {
    "id": 456,
    "message": "Document created successfully"
  }
]
```

## 🎓 Best Practices

1. **Always provide absolute paths** for `file_path`
2. **Validate files exist** before calling tools
3. **Use meaningful document names** (defaults to contract name)
4. **Handle warnings** in contract creation response
5. **Retry failed attachments** using standalone tool
6. **Check file permissions** before upload
7. **Consider file size limits** (GLPI may have restrictions)

## 🔐 Security Notes

- ✅ File path validation prevents directory traversal
- ✅ File existence checked before upload
- ✅ Uses existing GLPI authentication
- ⚠️ No file size limit enforced (consider adding)
- ⚠️ No file type validation (accepts any file)
- ⚠️ No virus scanning (consider for production)

## 📚 Related Documentation

- Full documentation: `docs/DOCUMENT_ATTACHMENT.md`
- Code examples: `examples/document_attachment_example.py`
- API reference: `glpi/documents.py` docstrings
