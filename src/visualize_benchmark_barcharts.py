import pandas as pd
import plotly.express as px
from pathlib import Path

def generate_bar_charts():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    csv_file_path = project_root / 'results' / 'benchmark_evaluation_engineering_scores.csv'
    
    design_chart_path = project_root / 'results' / 'design_scores_barchart.html'
    usability_chart_path = project_root / 'results' / 'usability_scores_barchart.html'

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

    if 'design_score_avg' not in df.columns or 'usability_score' not in df.columns:
        print("Error: CSV must contain 'design_score_avg' and 'usability_score' columns.")
        return

    avg_design_score = df['design_score_avg'].mean()
    avg_usability_score = df['usability_score'].mean()

    print("Generating Design Scores Bar Chart...")
    
    title_design = 'Benchmark Quality: Design Scores (S<sub>D</sub>)'
    label_design = 'Design Score (S<sub>D</sub>)'
    
    fig_design = px.bar(
        df,
        x='design_score_avg',
        y='benchmark_name',
        orientation='h',
        title=title_design,
        color='design_score_avg',
        text='design_score_avg',
        labels={'design_score_avg': label_design, 'benchmark_name': 'Benchmark'}
    )
    
    fig_design.add_vline(
        x=avg_design_score, 
        line_width=2, 
        line_dash="dash", 
        line_color="grey",
        annotation_text=f"Average: {avg_design_score:.2f}",
        annotation_position="bottom right"
    )
    
    fig_design.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='white',
        xaxis_title=label_design,
        yaxis_title=None
    )
    fig_design.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_design.write_html(design_chart_path)
    fig_design.show()

    print("Generating Usability Scores Bar Chart...")
    
    title_usability = 'Benchmark Quality: Usability Scores (S<sub>U</sub>)'
    label_usability = 'Usability Score (S<sub>U</sub>)'
    
    fig_usability = px.bar(
        df,
        x='usability_score',
        y='benchmark_name',
        orientation='h',
        title=title_usability,
        color='usability_score',
        text='usability_score',
        labels={'usability_score': label_usability, 'benchmark_name': 'Benchmark'}
    )

    fig_usability.add_vline(
        x=avg_usability_score, 
        line_width=2, 
        line_dash="dash", 
        line_color="grey",
        annotation_text=f"Average: {avg_usability_score:.2f}",
        annotation_position="bottom right"
    )
    
    fig_usability.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='white',
        xaxis_title=label_usability,
        yaxis_title=None
    )
    fig_usability.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_usability.write_html(usability_chart_path)
    fig_usability.show()

    print(f"Bar charts saved to {design_chart_path} and {usability_chart_path}")
    print("Run completed.")

if __name__ == "__main__":
    generate_bar_charts()