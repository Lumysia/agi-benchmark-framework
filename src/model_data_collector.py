import pandas as pd
from pathlib import Path
from typing import List


class DataCollector:
    def __init__(self, models: List[str], benchmarks: List[str], filepath: Path):
        self.filepath = filepath
        self.models = sorted(models)
        self.benchmarks = sorted(benchmarks)
        self.df = None

    def load_or_create_dataframe(self):
        if self.filepath.exists():
            print(f"Loading existing data from {self.filepath}")
            self.df = pd.read_csv(self.filepath).set_index("model")
        else:
            print(f"File not found. Creating new dataframe at {self.filepath}")
            self.df = pd.DataFrame(index=self.models, columns=self.benchmarks)

        self.df = self.df.reindex(index=self.models, columns=self.benchmarks)

    def collect_missing_data(self):
        print("--- Interactive Model Performance Collector ---")
        print(
            "Scanning for missing data. Please enter scores (or press Enter to skip)."
        )

        updated = False

        for model in self.models:
            for benchmark in self.benchmarks:
                if pd.isna(self.df.at[model, benchmark]):
                    prompt = f"  Enter score for {model} on {benchmark}: "
                    raw_input = input(prompt)

                    if raw_input.strip() == "":
                        continue

                    try:
                        score = float(raw_input)
                        self.df.at[model, benchmark] = score
                        print(f"    -> Saved {model} @ {benchmark} = {score}")
                        updated = True
                    except ValueError:
                        print(f"    -> Invalid input '{raw_input}'. Skipping.")

        if not updated:
            print("\nNo new data was entered.")

        print("Data collection complete.")

    def save_dataframe(self):
        self.df.reset_index().rename(columns={"index": "model"}).to_csv(
            self.filepath, index=False, float_format="%.1f"
        )
        print(f"Successfully updated {self.filepath}")

    def run(self):
        try:
            self.load_or_create_dataframe()
            self.collect_missing_data()
            self.save_dataframe()
        except KeyboardInterrupt:
            print("\n\nUpdate cancelled by user. Saving partial progress...")
            self.save_dataframe()


def get_benchmarks_from_data_dir(data_dir: Path) -> List[str]:
    yaml_files = list(data_dir.glob("*.yaml"))
    yml_files = list(data_dir.glob("*.yml"))

    benchmark_names = [f.stem for f in yaml_files + yml_files]

    if not benchmark_names:
        print(f"Warning: No .yaml or .yml files found in {data_dir}")
        return []

    return sorted(list(set(benchmark_names)))


if __name__ == "__main__":
    MODEL_LIST = [
        "GPT-5",
        "Grok 4",
        "Gemini 2.5 Pro",
        "Claude Opus 4.1",
        "DeepSeek-V2",
        "Qwen2-72B",
        "GLM-4",
    ]

    SCRIPT_DIR = Path(__file__).parent
    PROJECT_ROOT = SCRIPT_DIR.parent
    DATA_DIR = PROJECT_ROOT / "data"
    FILE_PATH = PROJECT_ROOT / "results" / "model_performance_data.csv"

    BENCHMARK_LIST = get_benchmarks_from_data_dir(DATA_DIR)

    if BENCHMARK_LIST:
        print(f"Found {len(BENCHMARK_LIST)} benchmarks in /data/: {BENCHMARK_LIST}")
        collector = DataCollector(MODEL_LIST, BENCHMARK_LIST, FILE_PATH)
        collector.run()
    else:
        print("Stopping script. No benchmarks to process.")
