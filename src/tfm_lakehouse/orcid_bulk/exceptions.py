class OrcidBulkError(Exception):
    """Base class for all ORCID bulk pipeline errors."""


class OrcidBulkChecksumError(OrcidBulkError):
    """Raised when the downloaded file's MD5 does not match the expected checksum."""
