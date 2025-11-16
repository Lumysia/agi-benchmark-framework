import pandas as pd
import plotly.express as px
from pathlib import Path


def generate_quality_visualization_interactive():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    csv_file_path = (
        project_root / "results" / "benchmark_evaluation_engineering_scores.csv"
    )
    output_html_path = project_root / "results" / "benchmark_quality_interactive.html"

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

    if "design_score_avg" not in df.columns or "usability_score" not in df.columns:
        print(
            "Error: CSV must contain 'design_score_avg' and 'usability_score' columns."
        )
        return

    df = df.rename(
        columns={
            "design_score_avg": r"Design Score ($S_D$)",
            "usability_score": r"Usability Score ($S_U$)",
        }
    )

    label_design = r"Design Score ($S_D$)"
    label_usability = r"Usability Score ($S_U$)"

    fig = px.scatter(
        df,
        x=label_design,
        y=label_usability,
        color="benchmark_name",
        hover_name="benchmark_name",
        hover_data={
            "benchmark_name": False,
            label_design: ":.2f",
            label_usability: ":.2f",
        },
        size=label_usability,
        size_max=15,
        title=r"Benchmark Quality Assessment: Design vs. Usability (Interactive)",
        labels={label_design: label_design, label_usability: label_usability},
    )

    avg_design = df[label_design].mean()
    avg_usability = df[label_usability].mean()

    fig.add_hline(
        y=avg_usability,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Avg. Usability ({avg_usability:.2f})",
        annotation_position="bottom right",
    )
    fig.add_vline(
        x=avg_design,
        line_dash="dash",
        line_color="grey",
        annotation_text=f"Avg. Design ({avg_design:.2f})",
        annotation_position="bottom right",
    )

    fig.update_layout(
        xaxis=dict(range=[0, 16], gridcolor="rgba(230, 230, 230, 0.7)", zeroline=False),
        yaxis=dict(range=[0, 16], gridcolor="rgba(230, 230, 230, 0.7)", zeroline=False),
        plot_bgcolor="white",
        font=dict(size=12),
    )

    output_html_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output_html_path, include_mathjax="cdn")

    print(f"Interactive visualization saved successfully to {output_html_path}")

    fig.show(auto_open=False)


if __name__ == "__main__":
    generate_quality_visualization_interactive()
