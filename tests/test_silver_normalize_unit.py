import pytest

from tfm_lakehouse.silver.normalize import (
    fold,
    normalize_doi,
    normalize_organization,
    normalize_person_name,
    normalize_title,
    organization_tokens,
    parse_int,
    token_jaccard,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Universitat Politècnica de València", "universitat politecnica de valencia"),
        ("GARCÍA-LÓPEZ", "garcia lopez"),
        ("  Ana   Luiza  ", "ana luiza"),
        ("J. A.", "j a"),
        ("", ""),
        (None, ""),
        ("---", ""),
    ],
)
def test_fold_lowercases_strips_accents_and_punctuation(text, expected):
    assert fold(text) == expected


def test_person_name_keys_survive_the_generator_name_variants():
    exact = normalize_person_name("José Luis", "Villacañas de Castro")
    stripped = normalize_person_name("Jose Luis", "Villacanas de Castro")
    upper = normalize_person_name("José Luis", "VILLACAÑAS DE CASTRO")
    initial = normalize_person_name("J.", "Villacañas de Castro")

    assert exact == stripped == upper
    assert exact.family_key == "villacanas"
    assert exact.given_initial == initial.given_initial == "j"
    assert exact.family_tokens == ("villacanas", "de", "castro")


@pytest.mark.parametrize(
    ("family", "key"),
    [("de la Torre", "torre"), ("Del Río", "rio"), ("van der Berg", "berg"), ("Martins Gomes", "martins")],
)
def test_family_key_skips_leading_particles(family, key):
    assert normalize_person_name("Ana", family).family_key == key


def test_person_name_with_missing_parts_yields_empty_keys():
    name = normalize_person_name(None, None)
    assert (name.given, name.family_tokens, name.family_key, name.given_initial) == ("", (), "", "")


def test_organization_normalization_ignores_case_accents_stopwords_and_appended_urls():
    plain = normalize_organization("Universitat Politècnica de València")
    assert plain == normalize_organization("universitat politecnica de valencia")
    assert normalize_organization("Instituto de Salud Carlos III; https://ror.org/00ca2c886") == normalize_organization(
        "Instituto de Salud Carlos III"
    )
    assert "de" not in organization_tokens("Universidad de Vigo")
    assert normalize_organization(None) == ""


def test_token_jaccard_scores_overlap_and_handles_empty_sets():
    campus = organization_tokens("Universidad Autonoma de Madrid Facultad de Ciencias")
    base = organization_tokens("Universidad Autónoma de Madrid")
    assert token_jaccard(base, base) == 1.0
    assert token_jaccard(base, campus) == pytest.approx(3 / 5)
    assert token_jaccard(base, organization_tokens("Universidad de Vigo")) < 0.5
    assert token_jaccard(frozenset(), base) == 0.0


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("10.1000/ABC", "10.1000/abc"),
        ("https://doi.org/10.1000/ABC", "10.1000/abc"),
        ("http://dx.doi.org/10.1000/abc", "10.1000/abc"),
        ("doi: 10.1000/abc ", "10.1000/abc"),
        ("not a doi", None),
        ("10.1000", None),
        ("", None),
        (None, None),
    ],
)
def test_normalize_doi(raw, expected):
    assert normalize_doi(raw) == expected


def test_normalize_title_folds():
    assert normalize_title("Indústria da Moda 4.0") == "industria da moda 4 0"


@pytest.mark.parametrize(
    ("value", "expected"),
    [("2024", 2024), (" 03 ", 3), (2024, 2024), ("", None), ("abc", None), (None, None), (True, None), (3.5, None)],
)
def test_parse_int_accepts_ints_and_digit_strings_only(value, expected):
    assert parse_int(value) == expected
