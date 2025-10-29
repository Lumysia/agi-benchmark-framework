import yaml
import os
from pathlib import Path
from typing import List, Dict, Any

def load_benchmarks_from_dir(directory: str) -> List[Dict[str, Any]]:
    benchmark_files = list(Path(directory).glob('*.yaml'))
    benchmark_files.extend(list(Path(directory).glob('*.yml')))
    
    loaded_benchmarks = []
    
    if not benchmark_files:
        print(f"Warning: No .yaml or .yml files found in {directory}")
        return []

    for filepath in benchmark_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                data['__filepath__'] = str(filepath.name)
                loaded_benchmarks.append(data)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {filepath.name}: {e}")
        except Exception as e:
            print(f"Error loading file {filepath.name}: {e}")
            
    return loaded_benchmarks

if __name__ == "__main__":
    data_dir = "../data"
    
    print(f"Loading benchmarks from: {data_dir}")
    benchmarks = load_benchmarks_from_dir(data_dir)
    
    if benchmarks:
        print(f"\nSuccessfully loaded {len(benchmarks)} benchmark(s):")
        for bench in benchmarks:
            print(f"- {bench['__filepath__']} (Name: {bench.get('benchmark_info', {}).get('name', 'N/A')})")