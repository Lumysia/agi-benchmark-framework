import pandas as pd
from .loader import load_benchmarks_from_dir
from typing import List, Dict, Any

DATA_DIR = "../data"

def flatten_benchmark_data(benchmarks: List[Dict[str, Any]]) -> pd.DataFrame:
    flattened_data = []

    for item in benchmarks:
        record = {
            'name': item.get('benchmark_info', {}).get('name'),
            'paradigm': item.get('benchmark_info', {}).get('paradigm'),
            
            'eng_reproducibility': item.get('evaluation_engineering', {}).get('implementation', {}).get('reproducibility'),
            'eng_contamination': item.get('evaluation_engineering', {}).get('maintenance', {}).get('contamination_status'),
            'eng_status': item.get('evaluation_engineering', {}).get('maintenance', {}).get('status'),
            
            'assess_static': item.get('capability_assessment', {}).get('static_knowledge', {}).get('evaluates'),
            'assess_process': item.get('capability_assessment', {}).get('process_orientation', {}).get('evaluates'),
            'assess_learning': item.get('capability_assessment', {}).get('learning_adaptability', {}).get('evaluates'),
            
            'learning_metrics': [
                metric.get('id') for metric in item.get('capability_assessment', {}).get('learning_adaptability', {}).get('metrics', [])
            ],
            
            'workflow_stages': len(
                item.get('capability_assessment', {}).get('process_orientation', {}).get('workflow_stages', [])
            )
        }
        
        record['has_bwt'] = 'BWT' in record['learning_metrics']
        record['has_fwt'] = 'FWT' in record['learning_metrics']
        
        flattened_data.append(record)
        
    return pd.DataFrame(flattened_data)

def run_analysis(df: pd.DataFrame):
    if df.empty:
        print("No data to analyze. Please populate the /data/ directory.")
        return

    print("--- UGF Analysis Report ---")

    print("\n### 1. Paradigm Distribution ###")
    paradigm_counts = df['paradigm'].value_counts()
    print(paradigm_counts.to_markdown(numalign="left", stralign="left"))

    print("\n### 2. Evaluation Engineering (Reproducibility) ###")
    repro_counts = df['eng_reproducibility'].value_counts()
    print(repro_counts.to_markdown(numalign="left", stralign="left"))

    print("\n### 3. Blind Spot Analysis: Dynamic Learning Metrics ###")
    learning_df = df[df['assess_learning'] == True]
    
    if learning_df.empty:
        print("SYSTEMIC GAP: No benchmarks found that evaluate 'Learning Adaptability'.")
    else:
        metrics_summary = {
            'Total Learning Benchmarks': len(learning_df),
            'Benchmarks measuring BWT': learning_df['has_bwt'].sum(),
            'Benchmarks measuring FWT': learning_df['has_fwt'].sum()
        }
        print(pd.Series(metrics_summary).to_markdown(numalign="left", stralign="left"))

    print("\n### 4. Process-Orientation Analysis ###")
    process_df = df[df['assess_process'] == True]
    
    if process_df.empty:
        print("SYSTEMIC GAP: No benchmarks found that evaluate 'Process-Orientation'.")
    else:
        process_summary = df.pivot_table(
            index='name', 
            values='workflow_stages', 
            aggfunc='sum'
        ).rename(columns={'workflow_stages': 'Workflow Stages'})
        
        print(process_summary.to_markdown(numalign="left", stralign="left"))

    print("\n--- End of Report ---")

if __name__ == "__main__":
    benchmarks = load_benchmarks_from_dir(DATA_DIR)
    
    if benchmarks:
        main_df = flatten_benchmark_data(benchmarks)
        
        print("--- Loaded Data Overview ---")
        print(main_df[['name', 'paradigm', 'eng_reproducibility', 'assess_learning']])
        print("\n")
        
        run_analysis(main_df)
