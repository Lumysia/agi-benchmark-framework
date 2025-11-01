# agi-benchmark-framework

A unified framework (UGF) for AGI benchmarking, integrating principles of Evaluation Engineering with continual and active learning paradigms.

## Project Goal

This repository implements the Unified AGI Framework (UGF), a metadata schema designed to catalog, compare, and analyze AGI benchmarks.

## Setup

You can set up your environment in these ways:

### GitHub Codespaces

This repository is configured for Dev Containers, allowing you to start a pre-configured environment in one click.

1.  Click the **Code** button on this repository's main page.
2.  Select the **Codespaces** tab.
3.  Click **Create codespace on main**.

The environment will build automatically. All dependencies (like PyYAML) will be pre-installed, and you can immediately proceed to the [**Usage**](#usage) section.

### Local Setup

If you prefer to work locally:

```bash
# Create and activate a virtual environment
python3 -m venv env && source env/bin/activate

# Install dependencies
pip3 install -r requirements.txt
```

## Usage

```bash
# Run the validator
cd src
python3 validator.py

# Run the better bench score calculator
cd src
python3 calculate_evaluation_scores.py

# Run the analysis
cd src
python3 analysis.py
```

If the validator runs without errors, all benchmark files in the `/data/` directory are correct.

## Workflow (How to Add a New Benchmark)

This is the primary workflow for this project:

1.  Create File: Add a new `.yaml` file to the `/data/` directory (e.g., `arc_agi_2.yaml`).
2.  Populate Data: Fill out the schema fields based on the benchmark's paper and documentation.
3.  Validate: Run `python3 src/validator.py` from the root directory.
4.  Fix Errors: If the validator fails, fix the errors in your `.yaml` file.
5.  Commit: Once the validator passes, commit new file.
