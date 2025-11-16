import pytest


@pytest.fixture
def mock_valid_benchmark_data():
    return {
        "__filepath__": "valid_benchmark.yaml",
        "benchmark_info": {
            "name": "Test Benchmark",
            "version": "1.0",
            "description": "A benchmark for testing.",
            "reference": "https://example.com",
        },
        "design": {
            "tested_capability_definition": {
                "score": 10,
                "justification": "Clear definition.",
            },
            "capability_to_task_translation": {"score": 5, "justification": "Partial."},
            "real_world_relevance": {"score": 15, "justification": "Very relevant."},
            "use_cases_and_personas": {"score": 0, "justification": "Not defined."},
            "domain_expert_involvement": {"score": 10, "justification": "Yes."},
            "domain_literature_integration": {"score": 5, "justification": "Some."},
            "score_interpretation": {"score": 15, "justification": "Done."},
            "informed_metric_choice": {"score": 10, "justification": "Done."},
            "metric_floors_ceilings": {"score": 5, "justification": "Partial."},
            "human_performance_level": {"score": 15, "justification": "Done."},
            "random_performance_level": {"score": 10, "justification": "Done."},
            "input_sensitivity": {"score": 0, "justification": "No."},
            "validated_automatic_evaluation": {"score": "n/a", "justification": "N/A."},
            "differences_to_related_benchmarks": {
                "score": 10,
                "justification": "Done.",
            },
        },
        "implementation": {
            "evaluation_code_available": {"score": 15, "justification": "Yes."},
            "replication_script": {"score": 10, "justification": "Yes."},
            "evaluation_data_accessible": {"score": 5, "justification": "Partial."},
            "api_evaluation_support": {"score": 0, "justification": "No."},
            "local_model_evaluation_support": {"score": 15, "justification": "Yes."},
            "guid_or_encryption": {"score": "null", "justification": "N/A."},
            "training_on_test_set_task": {"score": 10, "justification": "Done."},
            "sensitive_content_warnings": {"score": "None", "justification": "N/A."},
            "release_requirements": {"score": 5, "justification": "Minimal."},
            "build_status": {"score": 15, "justification": "Yes."},
            "requirements_file": {"score": 10, "justification": "Yes."},
            "quick_start_guide": {"score": 5, "justification": "Partial."},
            "statistical_significance": {"score": 0, "justification": "No."},
        },
        "documentation": {
            "inline_code_comments": {"score": 5, "justification": "Some."},
            "code_documentation": {"score": 10, "justification": "Good."},
            "peer_reviewed_venue": {"score": 0, "justification": "No."},
            "construction_process_documented": {"score": 15, "justification": "Yes."},
            "test_tasks_rationale_documented": {"score": 10, "justification": "Yes."},
            "normative_properties_documented": {
                "score": 5,
                "justification": "Briefly.",
            },
            "limitations_documented": {"score": 15, "justification": "Yes."},
            "data_collection_documented": {"score": 10, "justification": "Yes."},
            "evaluation_metric_documented": {"score": 15, "justification": "Yes."},
            "license_specified": {"score": 15, "justification": "Yes."},
            "persistent_identifier": {"score": 0, "justification": "No."},
            "standardized_metadata": {"score": 5, "justification": "Partial."},
            "data_sources_documented": {"score": 10, "justification": "Yes."},
            "data_preprocessing_documented": {"score": "n/a", "justification": "N/A."},
            "data_annotation_documented": {"score": 10, "justification": "Yes."},
            "data_representativeness_explained": {
                "score": 5,
                "justification": "Partial.",
            },
            "documentation_standard": {"score": 5, "justification": "Basic."},
        },
        "maintenance": {
            "code_usability_checked": {"score": 10, "justification": "Yes."},
            "feedback_channel": {"score": 15, "justification": "Yes."},
            "contact_person": {"score": 5, "justification": "Yes."},
        },
        "agi_cognitive_abilities": {
            "general_knowledge": {"score": 10, "justification": "Yes."},
            "reading_writing_ability": {"score": 15, "justification": "Yes."},
            "mathematical_ability": {"score": 5, "justification": "Basic."},
            "on_the_spot_reasoning": {"score": 10, "justification": "Yes."},
            "working_memory": {"score": 0, "justification": "No."},
            "long_term_memory_storage": {"score": "n/a", "justification": "N/A."},
            "long_term_memory_retrieval": {"score": 5, "justification": "Partial."},
            "visual_processing": {"score": 0, "justification": "No."},
            "auditory_processing": {"score": 0, "justification": "No."},
            "speed": {"score": 0, "justification": "No."},
        },
    }


@pytest.fixture
def mock_invalid_benchmark_data():
    return {
        "__filepath__": "invalid_benchmark.yaml",
        "benchmark_info": {
            "name": "Test Benchmark",
            "version": "1.0",
            "description": "",
            "reference": "https://example.com",
        },
        "design": {
            "tested_capability_definition": {
                "score": 99,
                "justification": "Invalid score.",
            }
        },
        "implementation": {"evaluation_code_available": {"score": 15}},
        "documentation": {"inline_code_comments": {"score": 5, "justification": ""}},
    }
