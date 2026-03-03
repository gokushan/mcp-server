"""Central location for error codes and descriptions."""

ERROR_CODES = {
    100: "Malformed or unreadable file",
    101: "File with possible prompt injection",
    102: "Extension not allowed",
    103: "Read path not allowed",
    104: "Path doesn't exist",
    105: "LLM timeout or cancelled"
}


class FileReadError(IOError):
    """Raised when a file exists and has an allowed extension but cannot be read
    or its content is malformed / not decodable (maps to error code 100)."""
    pass


class FileExtensionError(ValueError):
    """Raised when a file's extension is not in the allowed extensions list
    (maps to error code 102)."""
    pass


def get_error_response(code: int) -> dict:
    """Get error code and description as a dictionary."""
    return {
        "error_code": code,
        "error_description": ERROR_CODES.get(code, "Unknown error")
    }
