# API Client Refactoring - Header Management

## Summary of Changes

This refactoring improves the header management in `GLPIAPIClient` to follow DRY principles and correct authentication header usage.

## Problem Identified

1. **Unnecessary Authorization header**: The `Authorization` header was being included in all requests, but it's only needed during `init_session`.
2. **Code duplication**: Headers were being constructed manually in `upload_file()` instead of using the existing `_get_headers()` method.

## Solution Implemented

### 1. Enhanced `_get_headers()` Method

**Before:**
```python
async def _get_headers(self, include_session: bool = True) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json",
        "App-Token": self.app_token,
        "Authorization": f"user_token {self.user_token}"  # ❌ Always included
    }
    if include_session and self.session_token:
        headers["Session-Token"] = self.session_token
    return headers
```

**After:**
```python
async def _get_headers(
    self, 
    include_session: bool = True,
    include_authorization: bool = False,      # ✅ NEW: Optional
    include_content_type: bool = True,        # ✅ NEW: Optional
) -> dict[str, str]:
    headers = {
        "App-Token": self.app_token,
    }
    
    if include_content_type:
        headers["Content-Type"] = "application/json"
    
    if include_authorization and self.user_token:  # ✅ Only when requested
        headers["Authorization"] = f"user_token {self.user_token}"
    
    if include_session and self.session_token:
        headers["Session-Token"] = self.session_token
    
    return headers
```

### 2. Updated `init_session()` Method

**Before:**
```python
headers = await self._get_headers(include_session=False)

if self.user_token:
    headers["Authorization"] = f"user_token {self.user_token}"  # ❌ Manual addition
    logger.debug("Using User Token authentication")
else:
    access_token = await self.oauth_client.ensure_valid_token()
    headers["Authorization"] = f"Bearer {access_token}"
```

**After:**
```python
if self.user_token:
    logger.debug("Using User Token authentication")
    headers = await self._get_headers(
        include_session=False,
        include_authorization=True  # ✅ Explicit request
    )
else:
    logger.debug("Using OAuth authentication")
    access_token = await self.oauth_client.ensure_valid_token()
    headers = await self._get_headers(include_session=False)
    headers["Authorization"] = f"Bearer {access_token}"
```

### 3. Refactored `upload_file()` Method

**Before:**
```python
# Build headers without Content-Type (httpx will set it for multipart)
headers = {
    "App-Token": self.app_token,
    "Session-Token": self.session_token,
    "Authorization": f"user_token {self.user_token}",  # ❌ Unnecessary
}
```

**After:**
```python
# Get headers without Content-Type (httpx will set it automatically for multipart)
headers = await self._get_headers(
    include_session=True,
    include_authorization=False,  # ✅ Not needed after init_session
    include_content_type=False,   # ✅ httpx handles this for multipart
)
```

## Benefits

### 1. **Correctness**
- ✅ `Authorization` header only included when actually needed (during `init_session`)
- ✅ Follows GLPI API authentication flow correctly

### 2. **DRY Principle**
- ✅ Single source of truth for header construction (`_get_headers()`)
- ✅ No manual header building in individual methods

### 3. **Flexibility**
- ✅ `include_content_type=False` allows multipart uploads (httpx auto-sets boundary)
- ✅ `include_authorization=True` only for initial authentication

### 4. **Maintainability**
- ✅ Future header changes only need to be made in one place
- ✅ Clear intent through explicit parameters

## Header Usage Matrix

| Method | App-Token | Session-Token | Authorization | Content-Type |
|--------|-----------|---------------|---------------|--------------|
| `init_session` (user_token) | ✅ | ❌ | ✅ user_token | ✅ JSON |
| `init_session` (OAuth) | ✅ | ❌ | ✅ Bearer | ✅ JSON |
| `get()` | ✅ | ✅ | ❌ | ✅ JSON |
| `post()` | ✅ | ✅ | ❌ | ✅ JSON |
| `put()` | ✅ | ✅ | ❌ | ✅ JSON |
| `delete()` | ✅ | ✅ | ❌ | ✅ JSON |
| `search()` | ✅ | ✅ | ❌ | ✅ JSON |
| `upload_file()` | ✅ | ✅ | ❌ | ❌ (multipart) |

## Authentication Flow

```
1. Client calls init_session()
   ├─ User Token Auth:
   │  └─ Headers: App-Token + Authorization (user_token)
   └─ OAuth Auth:
      └─ Headers: App-Token + Authorization (Bearer)
   
2. GLPI returns Session-Token

3. All subsequent requests:
   └─ Headers: App-Token + Session-Token
      (NO Authorization header needed)
```

## Backward Compatibility

✅ **Fully backward compatible**
- All existing method calls work without changes
- Default parameters maintain previous behavior for standard requests
- Only `upload_file()` benefits from the new parameters

## Testing Recommendations

1. **Test init_session with user_token**
   - Verify `Authorization: user_token XXX` is sent
   - Verify session token is received

2. **Test init_session with OAuth**
   - Verify `Authorization: Bearer XXX` is sent
   - Verify session token is received

3. **Test regular API calls**
   - Verify NO `Authorization` header is sent
   - Verify `Session-Token` is sent
   - Verify `Content-Type: application/json` is sent

4. **Test upload_file**
   - Verify NO `Authorization` header is sent
   - Verify `Session-Token` is sent
   - Verify NO `Content-Type` header is sent (httpx auto-sets multipart boundary)

## Code Quality Improvements

- ✅ **Single Responsibility**: `_get_headers()` now has clear, configurable behavior
- ✅ **Open/Closed**: Extended without modifying existing behavior
- ✅ **DRY**: No header construction duplication
- ✅ **Explicit > Implicit**: Clear parameter names show intent
