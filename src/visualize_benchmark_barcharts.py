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

    print("Generating Design Scores Bar Chart with LaTeX...")
    
    title_design = r'Benchmark Quality: Design Scores ($S_D$)'
    label_design = r'Design Score ($S_D$)'
    
    fig_design = px.bar(
        df,
        x='design_score_avg',
        y='benchmark_name',
        orientation='h',
        title=title_design,
        color='design_score_avg',
        text='design_score_avg',
        labels={
            'design_score_avg': label_design,
            'benchmark_name': 'Benchmark'
        }
    )
    
    fig_design.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='white',
        xaxis_title=label_design,
        yaxis_title=None
    )
    fig_design.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_design.write_html(design_chart_path, include_mathjax='cdn')
    fig_design.show()

    print("Generating Usability Scores Bar Chart with LaTeX...")
    
    title_usability = r'Benchmark Quality: Usability Scores ($S_U$)'
    label_usability = r'Usability Score ($S_U$)'
    
    fig_usability = px.bar(
        df,
        x='usability_score',
        y='benchmark_name',
        orientation='h',
        title=title_usability,
        color='usability_score',
        text='usability_score',
        labels={
            'usability_score': label_usability,
            'benchmark_name': 'Benchmark'
        }
    )
    
    fig_usability.update_layout(
        yaxis={'categoryorder':'total ascending'},
        plot_bgcolor='white',
        xaxis_title=label_usability,
        yaxis_title=None
    )
    fig_usability.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_usability.write_html(usability_chart_path, include_mathjax='cdn')
    fig_usability.show()

    print(f"Bar charts with LaTeX saved to {design_chart_path} and {usability_chart_path}")
    print("Run completed. You can now open the HTML files manually in your browser.")

if __name__ == "__main__":
    generate_bar_charts()