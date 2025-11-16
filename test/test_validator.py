import pytest
from src.validator import UGFValidator


def assert_error_in_list(error_substring, error_list):
    found = any(error_substring in err for err in error_list)
    assert found, (
        f"Expected substring '{error_substring}' not found in any error: {error_list}"
    )


@pytest.fixture
def validator():
    return UGFValidator()


@pytest.mark.parametrize(
    "score, expected",
    [
        (0, True),
        (5, True),
        (10, True),
        (15, True),
        (None, True),
        ("n/a", True),
        ("N/A", True),
        ("null", True),
        ("None", True),
        ("10", True),
        (1, False),
        (99, False),
        ("foo", False),
        (2.5, False),
    ],
)
def test_validate_score(validator, score, expected):
    is_valid = validator._validate_score(score, "test.yaml", "test.criterion")
    assert is_valid == expected
    if not expected:
        assert len(validator.errors) == 1


def test_validate_benchmark_info_valid(validator, mock_valid_benchmark_data):
    is_valid = validator._validate_benchmark_info(
        mock_valid_benchmark_data, "test.yaml"
    )
    assert is_valid == True
    assert len(validator.errors) == 0


def test_validate_benchmark_info_missing_section(validator):
    data = {"__filepath__": "test.yaml"}
    is_valid = validator._validate_benchmark_info(data, "test.yaml")
    assert is_valid == False
    assert_error_in_list("'benchmark_info' section", validator.errors)


def test_validate_benchmark_info_missing_field(validator, mock_valid_benchmark_data):
    del mock_valid_benchmark_data["benchmark_info"]["name"]
    is_valid = validator._validate_benchmark_info(
        mock_valid_benchmark_data, "test.yaml"
    )
    assert is_valid == False
    assert_error_in_list("Missing required field 'name'", validator.errors)


def test_validate_benchmark_info_empty_field(validator, mock_valid_benchmark_data):
    mock_valid_benchmark_data["benchmark_info"]["name"] = ""
    is_valid = validator._validate_benchmark_info(
        mock_valid_benchmark_data, "test.yaml"
    )
    assert is_valid == False
    assert_error_in_list(
        "Field 'name' in 'benchmark_info' cannot be empty", validator.errors
    )


def test_validate_section_criteria_valid(validator, mock_valid_benchmark_data):
    is_valid = validator._validate_section_criteria(
        mock_valid_benchmark_data, "test.yaml", "design"
    )
    assert is_valid == True
    assert len(validator.errors) == 0


def test_validate_section_criteria_missing_section(validator):
    data = {"__filepath__": "test.yaml"}
    is_valid = validator._validate_section_criteria(data, "test.yaml", "design")
    assert is_valid == False
    assert_error_in_list("Missing or invalid 'design' section", validator.errors)


def test_validate_section_criteria_missing_criterion(
    validator, mock_valid_benchmark_data
):
    del mock_valid_benchmark_data["design"]["real_world_relevance"]
    is_valid = validator._validate_section_criteria(
        mock_valid_benchmark_data, "test.yaml", "design"
    )
    assert is_valid == False
    assert_error_in_list(
        "Missing criterion 'real_world_relevance' in 'design'", validator.errors
    )


def test_validate_section_criteria_missing_score(validator, mock_valid_benchmark_data):
    del mock_valid_benchmark_data["design"]["tested_capability_definition"]["score"]
    is_valid = validator._validate_section_criteria(
        mock_valid_benchmark_data, "test.yaml", "design"
    )
    assert is_valid == False
    assert_error_in_list(
        "Missing 'score' field for criterion 'tested_capability_definition'",
        validator.errors,
    )


def test_validate_section_criteria_invalid_score(validator, mock_valid_benchmark_data):
    mock_valid_benchmark_data["design"]["tested_capability_definition"]["score"] = 99
    is_valid = validator._validate_section_criteria(
        mock_valid_benchmark_data, "test.yaml", "design"
    )
    assert is_valid == False
    assert_error_in_list("Invalid score value '99'", validator.errors)


def test_validate_section_criteria_missing_justification(
    validator, mock_valid_benchmark_data
):
    del mock_valid_benchmark_data["design"]["tested_capability_definition"][
        "justification"
    ]
    is_valid = validator._validate_section_criteria(
        mock_valid_benchmark_data, "test.yaml", "design"
    )
    assert is_valid == False
    assert_error_in_list(
        "Missing 'justification' field for criterion 'tested_capability_definition'",
        validator.errors,
    )


def test_validate_section_criteria_empty_justification(
    validator, mock_valid_benchmark_data
):
    mock_valid_benchmark_data["design"]["tested_capability_definition"][
        "justification"
    ] = ""
    is_valid = validator._validate_section_criteria(
        mock_valid_benchmark_data, "test.yaml", "design"
    )
    assert is_valid == False
    assert_error_in_list(
        "Field 'justification' for criterion 'tested_capability_definition' in 'design' cannot be empty",
        validator.errors,
    )


def test_validate_benchmark_fully_valid(validator, mock_valid_benchmark_data):
    is_valid = validator.validate_benchmark(mock_valid_benchmark_data)
    assert is_valid == True
    assert validator.passed_count == 1
    assert validator.failed_count == 0
    assert len(validator.errors) == 0


def test_validate_benchmark_invalid(validator, mock_invalid_benchmark_data):
    is_valid = validator.validate_benchmark(mock_invalid_benchmark_data)
    assert is_valid == False
    assert validator.passed_count == 0
    assert validator.failed_count == 1
    assert len(validator.errors) > 0
    assert_error_in_list(
        "Field 'description' in 'benchmark_info' cannot be empty", validator.errors
    )
    assert_error_in_list(
        "Invalid score value '99' for criterion 'design.tested_capability_definition'",
        validator.errors,
    )
    assert_error_in_list(
        "Missing 'justification' field for criterion 'evaluation_code_available' in 'implementation'",
        validator.errors,
    )
    assert_error_in_list(
        "Field 'justification' for criterion 'inline_code_comments' in 'documentation' cannot be empty",
        validator.errors,
    )


def test_validate_benchmark_missing_top_level_section(
    validator, mock_valid_benchmark_data
):
    del mock_valid_benchmark_data["design"]
    is_valid = validator.validate_benchmark(mock_valid_benchmark_data)
    assert is_valid == False
    assert validator.failed_count == 1
    assert_error_in_list("Missing top-level section: 'design'", validator.errors)
