import pytest
from pathlib import Path
from unittest.mock import patch
from src.calculate_evaluation_scores import (
    extract_scores,
    calculate_average_score,
    calculate_usability_score,
    process_benchmark,
    load_yaml_file,
)


@pytest.fixture
def mock_benchmark_sections():
    return {
        "design": {
            "crit_1": {"score": 10, "justification": "..."},
            "crit_2": {"score": 5, "justification": "..."},
            "crit_3": {"score": "n/a", "justification": "..."},
            "crit_4": {"score": None, "justification": "..."},
            "crit_5": {"score": 15, "justification": "..."},
            "crit_6": {"score": "null", "justification": "..."},
        },
        "implementation": {
            "impl_1": {"score": 15, "justification": "..."},
            "impl_2": {"score": "None", "justification": "..."},
        },
        "empty_section": {},
        "malformed_section": {"crit_1": "just a string", "crit_2": {"no_score": "foo"}},
    }


def test_extract_scores(mock_benchmark_sections):
    design_scores = extract_scores(mock_benchmark_sections, "design")
    assert design_scores == {
        "crit_1": 10,
        "crit_2": 5,
        "crit_3": None,
        "crit_4": None,
        "crit_5": 15,
        "crit_6": None,
    }

    impl_scores = extract_scores(mock_benchmark_sections, "implementation")
    assert impl_scores == {"impl_1": 15, "impl_2": None}

    empty_scores = extract_scores(mock_benchmark_sections, "empty_section")
    assert empty_scores == {}

    malformed_scores = extract_scores(mock_benchmark_sections, "malformed_section")
    assert malformed_scores == {}

    missing_section_scores = extract_scores(
        mock_benchmark_sections, "non_existent_section"
    )
    assert missing_section_scores == {}


def test_calculate_average_score():
    scores_valid = {"a": 10, "b": 5, "c": 15}
    avg, count = calculate_average_score(scores_valid)
    assert avg == 10.0
    assert count == 3

    scores_mixed = {"a": 10, "b": None, "c": 5, "d": None, "e": 15}
    avg, count = calculate_average_score(scores_mixed)
    assert avg == 10.0
    assert count == 3

    scores_none = {"a": None, "b": None}
    avg, count = calculate_average_score(scores_none)
    assert avg == 0.0
    assert count == 0

    scores_empty = {}
    avg, count = calculate_average_score(scores_empty)
    assert avg == 0.0
    assert count == 0


def test_calculate_usability_score():
    sI, nI = 10.0, 5
    sDo, nDo = 8.0, 10
    sM, nM = 12.0, 3
    sCA, nCA = 9.0, 2

    expected_su = (10.0 * 5 + 8.0 * 10 + 12.0 * 3 + 9.0 * 2) / (5 + 10 + 3 + 2)
    
    su = calculate_usability_score(sI, sDo, sM, sCA, nI, nDo, nM, nCA)
    assert su == expected_su


def test_calculate_usability_score_division_by_zero():
    su = calculate_usability_score(10.0, 8.0, 12.0, 0.0, 0, 0, 0, 0)
    assert su == 0.0


@patch("src.calculate_evaluation_scores.load_yaml_file")
def test_process_benchmark(mock_load_yaml, mock_valid_benchmark_data):
    mock_load_yaml.return_value = mock_valid_benchmark_data

    test_path = Path("dummy/valid_benchmark.yaml")
    result = process_benchmark(test_path)

    assert result["benchmark_name"] == "Test Benchmark"

    assert (
        result["sD"] == (10 + 5 + 15 + 0 + 10 + 5 + 15 + 10 + 5 + 15 + 10 + 0 + 10) / 13
    )

    assert result["nI"] == 11
    assert result["sI"] == (15 + 10 + 5 + 0 + 15 + 10 + 5 + 15 + 10 + 5 + 0) / 11

    assert result["nDo"] == 16
    assert (
        result["sDo"]
        == (5 + 10 + 0 + 15 + 10 + 5 + 15 + 10 + 15 + 15 + 0 + 5 + 10 + 10 + 5 + 5) / 16
    )

    assert result["nM"] == 3
    assert result["sM"] == (10 + 15 + 5) / 3

    assert result["nCA"] == 9
    assert result["sCA"] == (10 + 15 + 5 + 10 + 0 + 5 + 0 + 0 + 0) / 9

    nI, nDo, nM, nCA = result["nI"], result["nDo"], result["nM"], result["nCA"]
    sI, sDo, sM, sCA = result["sI"], result["sDo"], result["sM"], result["sCA"]

    denominator = (nI + nDo + nM + nCA)
    if denominator == 0:
        expected_SU = 0.0
    else:
        expected_SU = (nI * sI + nDo * sDo + nM * sM + nCA * sCA) / denominator

    assert result["SU"] == pytest.approx(expected_SU)