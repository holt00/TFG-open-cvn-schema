class OrcidError(Exception):
    """Base class for all ORCID client errors."""


class OrcidValidationError(OrcidError):
    """Raised when an ORCID iD fails format or checksum validation."""


class OrcidApiError(OrcidError):
    """Raised when the ORCID API returns an unexpected non-2xx response."""

    def __init__(self, message: str, status_code: int, body: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class OrcidNotFoundError(OrcidApiError):
    """Raised when the ORCID API returns 404 for a well-formed iD."""
