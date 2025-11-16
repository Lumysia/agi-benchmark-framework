import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import yaml
from typing import List, Dict, Any


def load_benchmarks_from_dir(directory: Path) -> List[Dict[str, Any]]:
    benchmark_files = list(directory.glob("*.yaml")) + list(directory.glob("*.yml"))
    loaded_benchmarks = []
    for filepath in benchmark_files:
        with open(filepath, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            data["__benchmark_name__"] = data.get("benchmark_info", {}).get(
                "name", filepath.stem
            )
            loaded_benchmarks.append(data)
    return loaded_benchmarks


def process_data_for_details(
    benchmarks: List[Dict[str, Any]],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    summary_data = []
    detailed_scores = []

    def calculate_average_score(scores_dict: Dict[str, Any]) -> tuple[float, int]:
        valid_scores = [
            v["score"]
            for v in scores_dict.values()
            if isinstance(v, dict) and v.get("score") is not None
        ]
        if not valid_scores:
            return 0.0, 0
        return sum(valid_scores) / len(valid_scores), len(valid_scores)

    for bench in benchmarks:
        name = bench["__benchmark_name__"]

        all_sections = ["design", "implementation", "documentation", "maintenance"]
        for section_name in all_sections:
            section = bench.get(section_name, {})
            for criterion, value in section.items():
                if isinstance(value, dict):
                    detailed_scores.append(
                        {
                            "benchmark": name,
                            "category": section_name.capitalize(),
                            "criterion": criterion,
                            "score": value.get("score"),
                        }
                    )

        sI, nI = calculate_average_score(bench.get("implementation", {}))
        sDo, nDo = calculate_average_score(bench.get("documentation", {}))
        sM, nM = calculate_average_score(bench.get("maintenance", {}))
        sCA, _ = calculate_average_score(bench.get("agi_cognitive_abilities", {}))

        SU = (
            ((sI * nI) + (sDo * nDo) + (sM * nM)) / (nI + nDo + nM)
            if (nI + nDo + nM) > 0
            else 0
        )

        row = {"benchmark": name, "Usability": SU, "AGI Coverage": sCA}
        summary_data.append(row)

    df_summary = pd.DataFrame(summary_data)
    df_detailed = pd.DataFrame(detailed_scores).dropna(subset=["score"])

    return df_summary, df_detailed


def create_detailed_heatmap(df_detailed: pd.DataFrame) -> go.Figure:
    label_mapping = {
        "tested_capability_definition": "Tested Capability Definition",
        "capability_to_task_translation": "Capability-to-Task Translation",
        "real_world_relevance": "Real World Relevance",
        "use_cases_and_personas": "Use Cases and Personas",
        "domain_expert_involvement": "Domain Expert Involvement",
        "domain_literature_integration": "Domain Literature Integration",
        "score_interpretation": "Score Interpretation Guidance",
        "informed_metric_choice": "Informed Metric Choice",
        "metric_floors_ceilings": "Metric Floors/Ceilings",
        "human_performance_level": "Human Performance Level",
        "random_performance_level": "Random Performance Level",
        "input_sensitivity": "Input Sensitivity",
        "validated_automatic_evaluation": "Validated Automatic Evaluation",
        "differences_to_related_benchmarks": "Differences to Related Benchmarks",
        "evaluation_code_available": "Evaluation Code Available",
        "replication_script": "Replication Script",
        "evaluation_data_accessible": "Evaluation Data Accessible",
        "api_evaluation_support": "API Evaluation Support",
        "local_model_evaluation_support": "Local Model Evaluation Support",
        "guid_or_encryption": "GUID or Encryption",
        "training_on_test_set_task": "Training-on-Test-Set Task",
        "sensitive_content_warnings": "Sensitive Content Warnings",
        "release_requirements": "Release Requirements",
        "build_status": "Build Status",
        "requirements_file": "Requirements File",
        "quick_start_guide": "Quick-Start Guide",
        "statistical_significance": "Statistical Significance",
        "inline_code_comments": "Inline Code Comments",
        "code_documentation": "Code Documentation",
        "peer_reviewed_venue": "Peer-Reviewed Venue",
        "construction_process_documented": "Construction Process Documented",
        "test_tasks_rationale_documented": "Test Tasks Rationale Documented",
        "normative_properties_documented": "Normative Properties Documented",
        "limitations_documented": "Limitations Documented",
        "data_collection_documented": "Data Collection Documented",
        "evaluation_metric_documented": "Evaluation Metric Documented",
        "license_specified": "License Specified",
        "persistent_identifier": "Persistent Identifier (PID)",
        "standardized_metadata": "Standardized Metadata",
        "data_sources_documented": "Data Sources Documented",
        "data_preprocessing_documented": "Data Preprocessing Documented",
        "data_annotation_documented": "Data Annotation Documented",
        "data_representativeness_explained": "Data Representativeness Explained",
        "documentation_standard": "Documentation Standard",
        "code_usability_checked": "Code Usability Checked",
        "feedback_channel": "Feedback Channel",
        "contact_person": "Contact Person",
    }
    df_detailed["criterion_pretty"] = df_detailed["criterion"].map(label_mapping)

    pivot_df = df_detailed.pivot(
        index="criterion_pretty", columns="benchmark", values="score"
    )
    category_mapping = df_detailed.drop_duplicates(subset="criterion_pretty").set_index(
        "criterion_pretty"
    )["category"]
    pivot_df["category"] = pivot_df.index.map(category_mapping)

    category_order = ["Design", "Implementation", "Documentation", "Maintenance"]
    pivot_df = pivot_df.sort_values(
        by="category", key=lambda s: s.map({c: i for i, c in enumerate(category_order)})
    )
    pivot_df = pivot_df.drop(columns="category")

    fig = px.imshow(
        pivot_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdYlGn",
        range_color=[0, 15],
        labels=dict(x="Benchmark", y="BetterBench Criterion", color="Score"),
    )
    fig.update_layout(
        height=1400,
        title_text="<b>BetterBench Lifecycle Score Heatmap</b>",
        title_x=0.5,
        xaxis_tickangle=-45,
    )
    return fig


def create_strategic_quadrant_chart(df_summary: pd.DataFrame) -> go.Figure:
    avg_usability = df_summary["Usability"].mean()
    avg_coverage = df_summary["AGI Coverage"].mean()

    fig = px.scatter(
        df_summary,
        x="Usability",
        y="AGI Coverage",
        text="benchmark",
        color="benchmark",
        size=[10] * len(df_summary),
        size_max=20,
    )
    fig.update_traces(textposition="bottom center")

    fig.add_vline(x=avg_usability, line_width=1, line_dash="dash", line_color="grey")
    fig.add_hline(y=avg_coverage, line_width=1, line_dash="dash", line_color="grey")

    fig.update_layout(
        title_text="<b>UGF Strategic Quadrant</b>",
        title_x=0.5,
        xaxis_title="SE Usability Score (SU)",
        yaxis_title="AGI Cognitive Coverage Score",
        showlegend=False,
        annotations=[
            dict(
                x=0.98,
                y=0.98,
                xref="paper",
                yref="paper",
                text="Ideal: High Rigor, Broad Scope",
                showarrow=False,
                bgcolor="rgba(200, 255, 200, 0.4)",
            ),
            dict(
                x=0.02,
                y=0.98,
                xref="paper",
                yref="paper",
                text="Potential: Broad Scope, Low Rigor",
                showarrow=False,
                bgcolor="rgba(255, 255, 200, 0.4)",
                xanchor="left",
            ),
            dict(
                x=0.02,
                y=0.02,
                xref="paper",
                yref="paper",
                text="Needs Improvement",
                showarrow=False,
                bgcolor="rgba(255, 200, 200, 0.4)",
                xanchor="left",
                yanchor="bottom",
            ),
            dict(
                x=0.98,
                y=0.02,
                xref="paper",
                yref="paper",
                text="Specialized: High Rigor, Narrow Scope",
                showarrow=False,
                bgcolor="rgba(200, 200, 255, 0.4)",
                yanchor="bottom",
            ),
        ],
    )
    return fig


def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)

    print("1. Loading and processing benchmark data for detailed analysis...")
    benchmarks = load_benchmarks_from_dir(data_dir)
    if not benchmarks:
        print("No benchmark YAML files found. Exiting.")
        return
    df_summary, df_detailed = process_data_for_details(benchmarks)
    print(f"   Loaded and processed {len(benchmarks)} benchmarks.")

    print("\n2. Generating and saving detailed visualizations...")
    charts = {
        "4_detailed_heatmap": create_detailed_heatmap(df_detailed),
        "5_strategic_quadrant": create_strategic_quadrant_chart(df_summary),
    }
    for name, fig in charts.items():
        path = results_dir / f"{name}.html"
        fig.write_html(path)
        print(f"   - Saved: {path}")

    print("\nDetailed visualization generation complete.")


if __name__ == "__main__":
    main()
