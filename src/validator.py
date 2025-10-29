import sys
from typing import Dict, Any
from loader import load_benchmarks_from_dir

CORE_REQUIREMENTS = {
    'benchmark_info': ['name', 'paradigm', 'description'],
    'evaluation_engineering': ['implementation', 'maintenance'],
    'capability_assessment': ['static_knowledge', 'process_orientation', 'learning_adaptability']
}

PARADIGM_REQUIREMENTS = {
    'Process-Oriented': {
        'path': ('capability_assessment', 'process_orientation'),
        'fields': ['evaluates', 'workflow_stages']
    },
    'Continual-Learning': {
        'path': ('capability_assessment', 'learning_adaptability'),
        'fields': ['evaluates', 'learning_type', 'metrics']
    }
}

LEARNING_METRICS = {'BWT', 'FWT', 'ACC'}

class UGFValidator:
    def __init__(self):
        self.errors = []
        self.passed_count = 0
        self.failed_count = 0

    def _assert(self, condition: bool, filename: str, message: str):
        if not condition:
            self.errors.append(f"[{filename}] {message}")
            raise AssertionError(message)

    def _get_nested(self, data: Dict, path: tuple):
        temp = data
        for key in path:
            if key not in temp:
                return None
            temp = temp[key]
        return temp

    def validate_benchmark(self, data: Dict[str, Any]):
        filename = data.get('__filepath__', 'unknown_file')
        
        try:
            for section, fields in CORE_REQUIREMENTS.items():
                self._assert(section in data, filename, f"Missing top-level section: '{section}'")
                for field in fields:
                    self._assert(field in data[section], filename, f"Missing field '{field}' in '{section}'")

            paradigm = self._get_nested(data, ('benchmark_info', 'paradigm'))
            self._assert(paradigm is not None, filename, "Missing 'benchmark_info.paradigm'")

            if paradigm in PARADIGM_REQUIREMENTS:
                req = PARADIGM_REQUIREMENTS[paradigm]
                section_data = self._get_nested(data, req['path'])
                self._assert(section_data is not None, filename, f"Missing section for paradigm '{paradigm}'")
                
                for field in req['fields']:
                    self._assert(field in section_data, filename, f"Missing field '{field}' in '{paradigm}' section")
                
                if section_data.get('evaluates') is not True:
                     self._assert(False, filename, f"Field 'evaluates' must be 'true' for paradigm '{paradigm}'")

                if paradigm == 'Continual-Learning':
                    metrics = section_data.get('metrics', [])
                    metric_ids = {m.get('id') for m in metrics}
                    missing_metrics = LEARNING_METRICS - metric_ids
                    self._assert(not missing_metrics, filename, f"Missing required learning metrics: {missing_metrics}")

            self.passed_count += 1
            return True

        except AssertionError:
            self.failed_count += 1
            return False

    def run_validation(self, directory: str):
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
