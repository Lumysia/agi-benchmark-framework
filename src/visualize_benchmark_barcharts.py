import pandas as pd
import plotly.express as px
from pathlib import Path


def generate_bar_charts():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    csv_file_path = (
        project_root / "results" / "benchmark_evaluation_engineering_scores.csv"
    )

    design_chart_path = project_root / "results" / "design_scores_barchart.html"
    usability_chart_path = project_root / "results" / "usability_scores_barchart.html"
    agi_cognitive_chart_path = (
        project_root / "results" / "agi_cognitive_scores_barchart.html"
    )

    if not csv_file_path.exists():
        print(f"Error: CSV file not found at {csv_file_path}")
        print("Please run 'calculate_evaluation_scores.py' first.")
        return

    try:
        df = pd.read_csv(csv_file_path)
    except pd.errors.EmptyDataError:
        print(f"Error: The file {csv_file_path} is empty.")
        return

    if df.empty:
        print("CSV file is empty. No data to plot.")
        return

    required_columns = [
        "design_score_avg",
        "usability_score",
        "agi_cognitive_abilities_score_avg",
    ]
    if not all(col in df.columns for col in required_columns):
        print(f"Error: CSV must contain the following columns: {required_columns}")
        return

    avg_design_score = df["design_score_avg"].mean()
    avg_usability_score = df["usability_score"].mean()
    avg_agi_score = df["agi_cognitive_abilities_score_avg"].mean()

    print("Generating Design Scores Bar Chart...")
    title_design = "Benchmark Quality: Design Scores (S<sub>D</sub>)"
    label_design = "Design Score (S<sub>D</sub>)"
    fig_design = px.bar(
        df,
        x="design_score_avg",
        y="benchmark_name",
        orientation="h",
        title=title_design,
        color="design_score_avg",
        text="design_score_avg",
        labels={"design_score_avg": label_design, "benchmark_name": "Benchmark"},
    )
    fig_design.add_vline(
        x=avg_design_score,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Average: {avg_design_score:.2f}",
        annotation_position="bottom right",
    )
    fig_design.update_layout(
        yaxis={"categoryorder": "total ascending"},
        plot_bgcolor="white",
        xaxis_title=label_design,
        yaxis_title=None,
    )
    fig_design.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_design.write_html(design_chart_path)
    fig_design.show()

    print("Generating Usability Scores Bar Chart...")
    title_usability = "Benchmark Quality: Usability Scores (S<sub>U</sub>)"
    label_usability = "Usability Score (S<sub>U</sub>)"
    fig_usability = px.bar(
        df,
        x="usability_score",
        y="benchmark_name",
        orientation="h",
        title=title_usability,
        color="usability_score",
        text="usability_score",
        labels={"usability_score": label_usability, "benchmark_name": "Benchmark"},
    )
    fig_usability.add_vline(
        x=avg_usability_score,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Average: {avg_usability_score:.2f}",
        annotation_position="bottom right",
    )
    fig_usability.update_layout(
        yaxis={"categoryorder": "total ascending"},
        plot_bgcolor="white",
        xaxis_title=label_usability,
        yaxis_title=None,
    )
    fig_usability.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_usability.write_html(usability_chart_path)
    fig_usability.show()

    print("Generating AGI Cognitive Scores Bar Chart...")
    title_agi = "Benchmark Quality: AGI Cognitive Scores (S<sub>CA</sub>)"
    label_agi = "AGI Cognitive Score (S<sub>CA</sub>)"
    fig_agi = px.bar(
        df,
        x="agi_cognitive_abilities_score_avg",
        y="benchmark_name",
        orientation="h",
        title=title_agi,
        color="agi_cognitive_abilities_score_avg",
        text="agi_cognitive_abilities_score_avg",
        labels={
            "agi_cognitive_abilities_score_avg": label_agi,
            "benchmark_name": "Benchmark",
        },
    )
    fig_agi.add_vline(
        x=avg_agi_score,
        line_width=2,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Average: {avg_agi_score:.2f}",
        annotation_position="bottom right",
    )
    fig_agi.update_layout(
        yaxis={"categoryorder": "total ascending"},
        plot_bgcolor="white",
        xaxis_title=label_agi,
        yaxis_title=None,
    )
    fig_agi.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_agi.write_html(agi_cognitive_chart_path)
    fig_agi.show()

    print(
        f"All three bar charts saved to: {design_chart_path}, {usability_chart_path}, and {agi_cognitive_chart_path}"
    )
    print("Run completed.")


if __name__ == "__main__":
    generate_bar_charts()
