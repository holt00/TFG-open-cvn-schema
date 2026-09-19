class BronzeLandingError(RuntimeError):
    """Raised when a bronze landing run cannot complete."""


class BronzeRejectionThresholdError(BronzeLandingError):
    """Raised when too many records fail the landing-time structural check."""


class BronzeSourceNotReadyError(BronzeLandingError):
    """Raised when a source's local input is missing or incomplete."""
