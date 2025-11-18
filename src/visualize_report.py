import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import yaml
from typing import List, Dict, Any


def load_benchmarks_from_dir(directory: Path) -> List[Dict[str, Any]]:
    benchmark_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
    loaded_benchmarks = []
    for filepath in benchmark_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            data["__filename__"] = filepath.name
            data["__benchmark_name__"] = data.get("benchmark_info", {}).get(
                "name", filepath.stem
            )
            loaded_benchmarks.append(data)
    return loaded_benchmarks


def process_scores(benchmarks: List[Dict[str, Any]]) -> pd.DataFrame:
    processed_data = []

    def calculate_average_score(scores_dict: Dict[str, Any]) -> tuple[float, int]:
        valid_scores = []
        for v in scores_dict.values():
            score_val = v.get("score")
            if score_val is not None and str(score_val).lower() != 'n/a':
                try:
                    valid_scores.append(float(score_val))
                except ValueError:
                    pass
        
        if not valid_scores:
            return 0.0, 0
        return sum(valid_scores) / len(valid_scores), len(valid_scores)

    for bench in benchmarks:
        name = bench["__benchmark_name__"]

        design_scores = bench.get("design", {})
        impl_scores = bench.get("implementation", {})
        doc_scores = bench.get("documentation", {})
        maint_scores = bench.get("maintenance", {})
        agi_scores = bench.get("agi_cognitive_abilities", {})

        sD, _ = calculate_average_score(design_scores)
        sI, nI = calculate_average_score(impl_scores)
        sDo, nDo = calculate_average_score(doc_scores)
        sM, nM = calculate_average_score(maint_scores)
        sCA, _ = calculate_average_score(agi_scores)

        SU = (
            ((sI * nI) + (sDo * nDo) + (sM * nM)) / (nI + nDo + nM)
            if (nI + nDo + nM) > 0
            else 0
        )

        row = {"benchmark": name, "Design": sD, "Usability": SU, "AGI Coverage": sCA}

        for ability, value in agi_scores.items():
            row[f"agi_{ability}"] = value.get("score", 0)

        row["Implementation_Avg"] = sI
        row["Documentation_Avg"] = sDo
        row["Maintenance_Avg"] = sM

        processed_data.append(row)

    return pd.DataFrame(processed_data)


def create_overview_radar_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    categories = ["Design", "Usability", "AGI Coverage"]

    for i, row in df.iterrows():
        fig.add_trace(
            go.Scatterpolar(
                r=[row["Design"], row["Usability"], row["AGI Coverage"]],
                theta=categories,
                fill="toself",
                name=row["benchmark"],
            )
        )

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 15])),
        showlegend=True,
        title_text="<b>Overall Score Profile</b>",
        title_x=0.5,
    )
    return fig


def create_agi_profile_charts(df: pd.DataFrame) -> go.Figure:
    num_benchmarks = len(df)
    cols = 2
    rows = (num_benchmarks + cols - 1) // cols

    subplot_titles = df["benchmark"].tolist()
    fig = make_subplots(
        rows=rows,
        cols=cols,
        specs=[[{"type": "polar"}] * cols] * rows,
        subplot_titles=subplot_titles,
        vertical_spacing=0.15,
        horizontal_spacing=0.1,
    )

    agi_abilities = sorted([col for col in df.columns if col.startswith("agi_")])

    label_mapping = {
        "agi_general_knowledge": "Knowledge (K)",
        "agi_reading_writing_ability": "Read/Write (RW)",
        "agi_mathematical_ability": "Math (M)",
        "agi_on_the_spot_reasoning": "Reasoning (R)",
        "agi_working_memory": "Work Memory (WM)",
        "agi_long_term_memory_storage": "LTM Storage (MS)",
        "agi_long_term_memory_retrieval": "LTM Retrieval (MR)",
        "agi_visual_processing": "Visual (V)",
        "agi_auditory_processing": "Auditory (A)",
        "agi_speed": "Speed (S)",
    }

    theta = [label_mapping.get(ability, ability) for ability in agi_abilities]

    for i, (_, row_data) in enumerate(df.iterrows()):
        current_row = (i // cols) + 1
        current_col = (i % cols) + 1

        scores = row_data[agi_abilities].tolist()
        fig.add_trace(
            go.Scatterpolar(
                r=scores, theta=theta, fill="toself", name=row_data["benchmark"]
            ),
            row=current_row,
            col=current_col,
        )

    fig.update_layout(
        height=450 * rows,
        title_text="<b>AGI Cognitive Profile</b>",
        title_x=0.5,
        showlegend=False,
    )

    fig.update_polars(radialaxis=dict(visible=True, range=[0, 15]))

    return fig


def create_engineering_quality_charts(df: pd.DataFrame) -> go.Figure:
    categories = [
        "Design",
        "Implementation_Avg",
        "Documentation_Avg",
        "Maintenance_Avg",
    ]

    fig = go.Figure()
    for category in categories:
        fig.add_trace(
            go.Bar(x=df["benchmark"], y=df[category], name=category.replace("_Avg", ""))
        )

    fig.update_layout(
        barmode="group",
        title_text="<b>Engineering Quality Breakdown</b>",
        title_x=0.5,
        yaxis_title="Average Score (0-15)",
        xaxis_title="Benchmark",
    )
    return fig


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    results_dir = project_root / "results"

    results_dir.mkdir(exist_ok=True)

    print("1. Loading benchmark data...")
    benchmarks = load_benchmarks_from_dir(data_dir)
    if not benchmarks:
        print("No benchmark YAML files found. Exiting.")
        return
    print(f"   Loaded {len(benchmarks)} benchmarks.")

    print("2. Processing scores...")
    df_scores = process_scores(benchmarks)
    print("   Score processing complete.")
    print("\nProcessed Score Summary:")
    print(df_scores[["benchmark", "Design", "Usability", "AGI Coverage"]].round(2))

    print("\n3. Generating visualizations...")

    fig1 = create_overview_radar_chart(df_scores)
    fig1_path = results_dir / "1_overview_radar_chart.html"
    fig1.write_html(fig1_path)
    print(f"   - Saved: {fig1_path}")

    fig2 = create_agi_profile_charts(df_scores)
    fig2_path = results_dir / "2_agi_cognitive_profile.html"
    fig2.write_html(fig2_path)
    print(f"   - Saved: {fig2_path}")

    fig3 = create_engineering_quality_charts(df_scores)
    fig3_path = results_dir / "3_engineering_quality_breakdown.html"
    fig3.write_html(fig3_path)
    print(f"   - Saved: {fig3_path}")

    print(
        "\nVisualization generation complete. You can open the HTML files in your browser."
    )


if __name__ == "__main__":
    main()
