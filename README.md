# agi-benchmark-framework

A unified framework (UGF) for AGI benchmarking, integrating principles of Evaluation Engineering with continual and active learning paradigms.

## Project Goal

This repository implements the Unified AGI Framework (UGF), a metadata schema designed to catalog, compare, and analyze AGI benchmarks.

## Usage

```bash
# Create and activate a virtual environment
python3 -m venv env && source env/bin/activate

# Install dependencies
pip install PyYAML

# Run the validator
cd src
python3 validator.py
```

If the validator runs without errors, all benchmark files in the `/data/` directory are correct.

## Workflow (How to Add a New Benchmark)

This is the primary workflow for this project:

1.  Create File: Add a new `.yaml` file to the `/data/` directory (e.g., `arc_agi_2.yaml`).
2.  Populate Data: Fill out the schema fields based on the benchmark's paper and documentation.
3.  Validate: Run `python3 src/validator.py` from the root directory.
4.  Fix Errors: If the validator fails, fix the errors in your `.yaml` file.
5.  Commit: Once the validator passes, commit new file.
