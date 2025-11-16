#!/usr/bin/env python3
"""
Calculate BetterBench scores from YAML files and export to CSV.

This script reads all YAML files from the /data directory, extracts scores
for each criterion, calculates average scores (sI, sDo, sM) and usability
score (SU) according to the BetterBench methodology.

Output CSV contains:
- implementation_score_avg: Average points across implementation criteria (sI)
- documentation_score_avg: Average points across documentation criteria (sDo)
- maintenance_score_avg: Average points across maintenance criteria (sM)
- implementation_criteria_count: Number of non-n/a implementation criteria (nI)
- documentation_criteria_count: Number of non-n/a documentation criteria (nDo)
- maintenance_criteria_count: Number of non-n/a maintenance criteria (nM)
- usability_score: Weighted average usability score (SU) = (nI*sI + nDo*sDo + nM*sM)/(nI + nDo + nM)
- design_score_avg: Average points across design criteria (sD)
- agi_cognitive_abilities_score_avg: Average points across AGI cognitive abilities criteria (sCA)
- agi_cognitive_abilities_criteria_count: Number of non-n/a AGI cognitive abilities criteria (nCA)
"""

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_scores(data: Dict[str, Any], section: str) -> Dict[str, Optional[int]]:
    """
    Extract scores from a section (design, implementation, documentation, maintenance, agi_cognitive_abilities).

    Returns a dictionary mapping criterion names to their scores.
    """
    scores = {}
    if section in data:
        for criterion, value in data[section].items():
            if isinstance(value, dict) and "score" in value:
                score = value["score"]
                # Convert null/None to None, keep integers as is
                if score is None or (
                    isinstance(score, str) and score.lower() in ["null", "n/a", "na"]
                ):
                    scores[criterion] = None
                elif isinstance(score, (int, float)):
                    scores[criterion] = int(score)
                else:
                    scores[criterion] = None
    return scores


def calculate_average_score(scores: Dict[str, Optional[int]]) -> tuple[float, int]:
    """
    Calculate average score excluding None/null values.

    Returns:
        (average_score, count_of_valid_scores)
    """
    valid_scores = [score for score in scores.values() if score is not None]
    if not valid_scores:
        return 0.0, 0
    return sum(valid_scores) / len(valid_scores), len(valid_scores)


def calculate_usability_score(
    sI: float, sDo: float, sM: float, nI: int, nDo: int, nM: int
) -> float:
    """
    Calculate usability score SU using the formula:
    SU = (nI*sI + nDo*sDo + nM*sM)/(nI + nDo + nM)
    """
    if (nI + nDo + nM) == 0:
        return 0.0
    return (nI * sI + nDo * sDo + nM * sM) / (nI + nDo + nM)


def process_benchmark(file_path: Path) -> Dict[str, Any]:
    """Process a single benchmark YAML file and extract all relevant data."""
    data = load_yaml_file(file_path)

    # Extract benchmark info
    benchmark_name = data.get("benchmark_info", {}).get("name", file_path.stem)

    # Extract scores from each section
    design_scores = extract_scores(data, "design")
    implementation_scores = extract_scores(data, "implementation")
    documentation_scores = extract_scores(data, "documentation")
    maintenance_scores = extract_scores(data, "maintenance")
    cognitive_abilities_scores = extract_scores(data, "agi_cognitive_abilities")

    # Calculate averages (subscores)
    sD, nD = calculate_average_score(design_scores)
    sI, nI = calculate_average_score(implementation_scores)
    sDo, nDo = calculate_average_score(documentation_scores)
    sM, nM = calculate_average_score(maintenance_scores)
    sCA, nCA = calculate_average_score(cognitive_abilities_scores)

    # Calculate usability score
    SU = calculate_usability_score(sI, sDo, sM, nI, nDo, nM)

    return {
        "benchmark_name": benchmark_name,
        "sI": sI,
        "sDo": sDo,
        "sM": sM,
        "SU": SU,
        "sD": sD,
        "sCA": sCA,
        "nI": nI,
        "nDo": nDo,
        "nM": nM,
        "nCA": nCA,
    }


def write_csv(results: List[Dict[str, Any]], output_file: Path):
    """Write results to CSV file with only summary scores."""
    # CSV headers - clear descriptive names
    headers = [
        "benchmark_name",
        "implementation_score_avg",  # sI: Average points across implementation criteria
        "documentation_score_avg",  # sDo: Average points across documentation criteria
        "maintenance_score_avg",  # sM: Average points across maintenance criteria
        "implementation_criteria_count",  # nI: Number of implementation criteria (not n/a)
        "documentation_criteria_count",  # nDo: Number of documentation criteria (not n/a)
        "maintenance_criteria_count",  # nM: Number of maintenance criteria (not n/a)
        "usability_score",  # SU: Weighted average usability score
        "design_score_avg",  # sD: Average points across design criteria
        "agi_cognitive_abilities_score_avg",  # sCA: Average points across AGI cognitive abilities criteria
        "agi_cognitive_abilities_criteria_count",  # nCA: Number of AGI cognitive abilities criteria (not n/a)
    ]

    # Ensure output directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for result in results:
            row = [
                result["benchmark_name"],
                round(result["sI"], 2),  # Implementation score (average)
                round(result["sDo"], 2),  # Documentation score (average)
                round(result["sM"], 2),  # Maintenance score (average)
                result["nI"],  # Count of implementation criteria
                result["nDo"],  # Count of documentation criteria
                result["nM"],  # Count of maintenance criteria
                round(result["SU"], 2),  # Usability score
                round(result["sD"], 2),  # Design score (average)
                round(result["sCA"], 2),  # Cognitive abilities score (average)
                result["nCA"],  # Count of cognitive abilities criteria
            ]
            writer.writerow(row)


def main():
    """Main function to process all YAML files and generate CSV."""
    # Get the project root directory (assuming script is in /src)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    output_file = (
        project_root / "results" / "benchmark_evaluation_engineering_scores.csv"
    )

    # Check if data directory exists
    if not data_dir.exists():
        print(f"Error: Data directory not found at {data_dir}")
        return

    # Find all YAML files
    yaml_files = sorted(data_dir.glob("*.yaml"))

    if not yaml_files:
        print(f"No YAML files found in {data_dir}")
        return

    print(f"Processing {len(yaml_files)} YAML files...")

    # Process each benchmark
    results = []
    for yaml_file in yaml_files:
        print(f"  Processing {yaml_file.name}...")
        try:
            result = process_benchmark(yaml_file)
            results.append(result)
        except Exception as e:
            print(f"    Error processing {yaml_file.name}: {e}")
            continue

    # Write CSV
    write_csv(results, output_file)
    print(f"\nCSV file written to: {output_file}")
    print(f"Processed {len(results)} benchmarks successfully.")


if __name__ == "__main__":
    main()
