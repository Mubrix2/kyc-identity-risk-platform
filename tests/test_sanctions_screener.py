# tests/test_sanctions_screener.py
import pytest
from app.core import sanctions_screener as screener


@pytest.fixture(scope="module", autouse=True)
def load_lists():
    loaded = screener.load_screening_lists()
    if not loaded:
        pytest.skip("Run download_sanctions_data.py first")


def test_exact_sanctions_match():
    # "ABBAS, ABU" is a real entry in the downloaded OFAC list
    result = screener.screen_sanctions("ABBAS, ABU")
    assert result["is_match"] is True
    assert result["program"] is not None


def test_no_match_for_unrelated_name():
    result = screener.screen_sanctions("RANDOM UNRELATED PERSON XYZ")
    assert result["is_match"] is False


def test_pep_match():
    result = screener.screen_pep("ADEBAYO JOHNSON")
    assert result["is_match"] is True
    assert result["category"] == "Head of State (Former)"


def test_combined_screening_flags_edd():
    result = screener.screen_individual("ABBAS, ABU")
    assert result["requires_edd"] is True
    assert result["sanctions"]["is_match"] is True


def test_combined_screening_clean_name():
    result = screener.screen_individual("RANDOM UNRELATED PERSON XYZ")
    assert result["requires_edd"] is False