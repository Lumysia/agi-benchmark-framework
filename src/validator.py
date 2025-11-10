import sys
from typing import Dict, Any, List, Set, Optional
from .loader import load_benchmarks_from_dir

# Required top-level sections
REQUIRED_SECTIONS = ['benchmark_info', 'design', 'implementation', 'documentation', 'maintenance']

# Required fields in benchmark_info
BENCHMARK_INFO_REQUIRED = ['name', 'version', 'description', 'reference']

# All criteria for each section (based on ugf_schema_blank.yaml)
DESIGN_CRITERIA = [
    'tested_capability_definition',
    'capability_to_task_translation',
    'real_world_relevance',
    'use_cases_and_personas',
    'domain_expert_involvement',
    'domain_literature_integration',
    'score_interpretation',
    'informed_metric_choice',
    'metric_floors_ceilings',
    'human_performance_level',
    'random_performance_level',
    'input_sensitivity',
    'validated_automatic_evaluation',
    'differences_to_related_benchmarks'
]

IMPLEMENTATION_CRITERIA = [
    'evaluation_code_available',
    'replication_script',
    'evaluation_data_accessible',
    'api_evaluation_support',
    'local_model_evaluation_support',
    'guid_or_encryption',
    'training_on_test_set_task',
    'sensitive_content_warnings',
    'release_requirements',
    'build_status',
    'requirements_file',
    'quick_start_guide',
    'statistical_significance'
]

DOCUMENTATION_CRITERIA = [
    'inline_code_comments',
    'code_documentation',
    'peer_reviewed_venue',
    'construction_process_documented',
    'test_tasks_rationale_documented',
    'normative_properties_documented',
    'limitations_documented',
    'data_collection_documented',
    'evaluation_metric_documented',
    'license_specified',
    'persistent_identifier',
    'standardized_metadata',
    'data_sources_documented',
    'data_preprocessing_documented',
    'data_annotation_documented',
    'data_representativeness_explained',
    'documentation_standard'
]

MAINTENANCE_CRITERIA = [
    'code_usability_checked',
    'feedback_channel',
    'contact_person'
]

AGI_COGNITIVE_ABILITIES_CRITERIA = [
    'general_knowledge',
    'reading_writing_ability',
    'mathematical_ability',
    'on_the_spot_reasoning',
    'working_memory',
    'long_term_memory_storage',
    'long_term_memory_retrieval',
    'visual_processing',
    'auditory_processing',
    'speed'
]

# All criteria grouped by section
SECTION_CRITERIA = {
    'design': DESIGN_CRITERIA,
    'implementation': IMPLEMENTATION_CRITERIA,
    'documentation': DOCUMENTATION_CRITERIA,
    'maintenance': MAINTENANCE_CRITERIA,
    'agi_cognitive_abilities': AGI_COGNITIVE_ABILITIES_CRITERIA
}

# Valid score values
VALID_SCORES = {0, 5, 10, 15}
VALID_SCORE_STRINGS = {'n/a', 'null', 'None'}


class UGFValidator:
    def __init__(self):
        self.errors = []
        self.passed_count = 0
        self.failed_count = 0

    def _add_error(self, filename: str, message: str):
        """Add an error message without raising an exception."""
        self.errors.append(f"[{filename}] {message}")

    def _get_nested(self, data: Dict, path: tuple) -> Optional[Any]:
        """Safely navigate nested dictionary structure."""
        temp = data
        for key in path:
            if not isinstance(temp, dict) or key not in temp:
                return None
            temp = temp[key]
        return temp

    def _validate_score(self, score: Any, filename: str, criterion: str) -> bool:
        """Validate that score is a valid value (null, n/a, or 0-15)."""
        if score is None:
            return True  # null is valid
        if isinstance(score, str):
            if score.lower() in ['n/a', 'null', 'none']:
                return True
            try:
                score_int = int(score)
                if score_int in VALID_SCORES:
                    return True
            except ValueError:
                pass
        elif isinstance(score, int):
            if score in VALID_SCORES:
                return True
        self._add_error(filename, f"Invalid score value '{score}' for criterion '{criterion}'. Must be null, 'n/a', or one of {sorted(VALID_SCORES)}")
        return False

    def _validate_benchmark_info(self, data: Dict[str, Any], filename: str) -> bool:
        """Validate benchmark_info section."""
        valid = True
        benchmark_info = data.get('benchmark_info')
        
        if not isinstance(benchmark_info, dict):
            self._add_error(filename, "Missing or invalid 'benchmark_info' section")
            return False
        
        for field in BENCHMARK_INFO_REQUIRED:
            if field not in benchmark_info:
                self._add_error(filename, f"Missing required field '{field}' in 'benchmark_info'")
                valid = False
            elif not benchmark_info[field]:
                self._add_error(filename, f"Field '{field}' in 'benchmark_info' cannot be empty")
                valid = False
        
        return valid

    def _validate_section_criteria(self, data: Dict[str, Any], filename: str, section: str) -> bool:
        """Validate that all criteria in a section have score and justification."""
        valid = True
        section_data = data.get(section)
        
        if not isinstance(section_data, dict):
            self._add_error(filename, f"Missing or invalid '{section}' section")
            return False
        
        expected_criteria = SECTION_CRITERIA.get(section, [])
        
        # Check that each expected criterion exists and has required fields
        for criterion in expected_criteria:
            if criterion not in section_data:
                self._add_error(filename, f"Missing criterion '{criterion}' in '{section}' section")
                valid = False
                continue
            
            criterion_data = section_data[criterion]
            if not isinstance(criterion_data, dict):
                self._add_error(filename, f"Criterion '{criterion}' in '{section}' must be a dictionary")
                valid = False
                continue
            
            # Check for required fields: score and justification
            if 'score' not in criterion_data:
                self._add_error(filename, f"Missing 'score' field for criterion '{criterion}' in '{section}'")
                valid = False
            else:
                # Validate score value
                if not self._validate_score(criterion_data['score'], filename, f"{section}.{criterion}"):
                    valid = False
            
            if 'justification' not in criterion_data:
                self._add_error(filename, f"Missing 'justification' field for criterion '{criterion}' in '{section}'")
                valid = False
            elif not criterion_data['justification']:
                self._add_error(filename, f"Field 'justification' for criterion '{criterion}' in '{section}' cannot be empty")
                valid = False
        
        # Warn about extra criteria that are not in the schema (optional check)
        # This is commented out as it might be too strict - uncomment if needed
        # for criterion in section_data:
        #     if criterion not in expected_criteria:
        #         self._add_error(filename, f"Unknown criterion '{criterion}' in '{section}' section")
        #         valid = False
        
        return valid

    def validate_benchmark(self, data: Dict[str, Any]) -> bool:
        """Validate a single benchmark against the UGF schema."""
        filename = data.get('__filepath__', 'unknown_file')
        valid = True
        
        # Check for required top-level sections
        for section in REQUIRED_SECTIONS:
            if section not in data:
                self._add_error(filename, f"Missing top-level section: '{section}'")
                valid = False
        
        # Validate benchmark_info
        if 'benchmark_info' in data:
            if not self._validate_benchmark_info(data, filename):
                valid = False
        
        # Validate each section's criteria
        for section in ['design', 'implementation', 'documentation', 'maintenance', 'agi_cognitive_abilities']:
            if section in data:
                if not self._validate_section_criteria(data, filename, section):
                    valid = False
        
        if valid:
            self.passed_count += 1
        else:
            self.failed_count += 1
        
        return valid

    def run_validation(self, directory: str):
        """Run validation on all benchmarks in a directory."""
        benchmarks = load_benchmarks_from_dir(directory)
        
        if not benchmarks:
            print(f"No benchmarks found in {directory} to validate.")
            return
        
        print(f"Starting validation for {len(benchmarks)} benchmark(s)...\n")
        
        for bench_data in benchmarks:
            self.validate_benchmark(bench_data)
        
        print("\n--- Validation Summary ---")
        if self.errors:
            print(f"\nReported Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"- {error}")
        
        print(f"\nPassed: {self.passed_count}")
        print(f"Failed: {self.failed_count}")
        print("--------------------------")
        
        if self.failed_count > 0:
            sys.exit(1)
        else:
            print("All benchmarks passed validation.")


if __name__ == "__main__":
    data_dir = "../data"
    validator = UGFValidator()
    validator.run_validation(data_dir)
