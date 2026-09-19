class SyntheticCvnSeedError(RuntimeError):
    """Raised when the ORCID seed directory cannot provide usable seeds."""


class SyntheticCvnGenerationError(RuntimeError):
    """Raised when the generator cannot produce the requested number of valid documents."""
