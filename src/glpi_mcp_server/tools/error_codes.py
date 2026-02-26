"""Central location for error codes and descriptions."""

ERROR_CODES = {
    100: "Malformed or unreadable file",
    101: "File with possible prompt injection",
    102: "Extension not allowed",
    103: "Read path not allowed",
    104: "Path doesn't exist"

}

def get_error_response(code: int) -> dict:
    """Get error code and description as a dictionary."""
    return {
        "error_code": code,
        "error_description": ERROR_CODES.get(code, "Unknown error")
    }
