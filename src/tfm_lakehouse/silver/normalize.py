from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

# Leading family-name particles are skipped when picking the token that keys a
# family name ("de la Torre" is keyed by "torre"), so that they do not put every
# such surname in one block.
_PARTICLES = frozenset(
    {"de", "del", "la", "las", "los", "el", "van", "von", "der", "den", "da", "do", "dos", "das", "di", "du", "le", "y", "i"}
)

# Words that carry no identity in an organization name, in the languages the
# ORCID Spain subset mixes (Spanish, Catalan, Galician, Basque, Portuguese,
# English).
_ORGANIZATION_STOPWORDS = frozenset(
    {"de", "del", "la", "las", "los", "el", "of", "the", "and", "y", "i", "e", "da", "do", "dos", "das", "di", "en", "et", "for", "at"}
)

_URL = re.compile(r"https?://\S+", re.IGNORECASE)
_NON_ALNUM = re.compile(r"[^0-9a-z]+")
_DOI_PREFIX = re.compile(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", re.IGNORECASE)


@dataclass(frozen=True)
class NormalizedName:
    """A person name reduced to the keys entity resolution compares.

    Args:
        given: Folded given names ("jose luis").
        family_tokens: Folded family-name tokens, in order.
        family_key: First family token that is not a particle; the blocking key.
        given_initial: First letter of the folded given names, or "".
    """

    given: str
    family_tokens: tuple[str, ...]
    family_key: str
    given_initial: str

    @property
    def family(self) -> str:
        return " ".join(self.family_tokens)


def fold(text: str | None) -> str:
    """Lower-case ``text``, strip accents and punctuation, collapse whitespace.

    Args:
        text: Any string, or None.

    Returns:
        Only ``[0-9a-z]`` tokens separated by single spaces; "" for None or a
        string without alphanumerics.
    """
    if not text:
        return ""
    decomposed = unicodedata.normalize("NFKD", text)
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return _NON_ALNUM.sub(" ", without_marks.casefold()).strip()


def normalize_person_name(given_names: str | None, family_name: str | None) -> NormalizedName:
    """Reduce a name to its comparison keys.

    Args:
        given_names: Given names as written in the source.
        family_name: Family name(s) as written in the source.

    Returns:
        The normalized name; empty fields become "" or an empty tuple.
    """
    given = fold(given_names)
    family_tokens = tuple(fold(family_name).split())
    family_key = next((token for token in family_tokens if token not in _PARTICLES), family_tokens[0] if family_tokens else "")
    return NormalizedName(given=given, family_tokens=family_tokens, family_key=family_key, given_initial=given[:1])


def organization_tokens(name: str | None) -> frozenset[str]:
    """Return the identity-carrying tokens of an organization name.

    URLs (ORCID sometimes appends a ROR link to the name) and stop words are
    dropped, accents and case are folded.
    """
    without_urls = _URL.sub(" ", name or "")
    return frozenset(token for token in fold(without_urls).split() if token not in _ORGANIZATION_STOPWORDS)


def normalize_organization(name: str | None) -> str:
    """Return a canonical string for an organization name (sorted tokens)."""
    return " ".join(sorted(organization_tokens(name)))


def token_jaccard(left: frozenset[str], right: frozenset[str]) -> float:
    """Jaccard similarity of two token sets; 0.0 when either is empty."""
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def normalize_title(title: str | None) -> str:
    """Fold a publication title for comparison."""
    return fold(title)


def normalize_doi(doi: str | None) -> str | None:
    """Return a DOI in its canonical lower-case form, or None if it is not one.

    Strips the ``https://doi.org/`` / ``doi:`` prefixes and surrounding
    whitespace. A value that does not start with ``10.`` afterwards is not a DOI.
    """
    if not doi:
        return None
    candidate = _DOI_PREFIX.sub("", doi.strip()).strip().lower()
    return candidate if candidate.startswith("10.") and "/" in candidate else None


def parse_int(value: object) -> int | None:
    """Return ``value`` as an int when it is an int or a digit string, else None.

    Dates reach silver as strings (issue #96) or integers (the XML importer);
    both are accepted. Booleans are not numbers here.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None
