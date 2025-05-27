import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
'''
# Optimized association rule analysis using pre-loaded dataframe
def analyze_binary_association_rules(binary_df, min_support=0.1, min_threshold=0.7):
    frequent_itemsets = apriori(binary_df, min_support=min_support, use_colnames=True)
    return association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)

def visualize_rules(rules_df, image):
    top_rules = rules_df.nlargest(10, 'lift') if len(rules_df) > 10 else rules_df
    labels = [
        f"{list(row.antecedents)} → {list(row.consequents)}"
        for _, row in top_rules.iterrows()
    ]
    
    plt.figure(figsize=(12, len(labels) * 0.5 + 2))
    sns.barplot(x='lift', y=np.arange(len(labels)), data=top_rules, orient='h')
    plt.yticks(np.arange(len(labels)), labels)
    plt.title('Top Association Rules by Lift')
    plt.tight_layout()
    plt.savefig(image)
    plt.close()

def analyze_real_data(data, min_support=0.5, min_confidence=0.7, image="association_rules.png"):  # Increased default thresholds
    # Convert to boolean type and sparse representation
    if not np.isin(data.values, [True, False]).all():
        print("Converting to boolean (True=present, False=missing)")
        data = data.notna()
    
    # Convert to sparse DataFrame to save memory
    data = data.astype(pd.SparseDtype(bool, fill_value=False))
    
    if len(data) > 5000:
        print("Sampling 100k transactions for analysis")
        data = data.sample(n=5000, random_state=42)

    print(f"Analyzing data: {data.shape[0]} rows, {data.shape[1]} columns")
    
    # Column pruning - remove columns with < min_support presence
    col_support = data.mean()
    keep_cols = col_support[col_support >= min_support].index
    data = data[keep_cols]
    print(f"Kept {len(keep_cols)} columns after pruning")

    # Transaction filtering - remove empty transactions
    row_counts = data.sum(axis=1)
    data = data[row_counts > 0]
    print(f"Kept {len(data)} non-empty transactions")

    # If still too large, sample the data
    if len(data) > 5000:
        print("Sampling 5k transactions for analysis")
        data = data.sample(n=5000, random_state=42)

    # Generate rules with optimized parameters
    try:
        frequent_itemsets = apriori(
            data,
            min_support=min_support,
            use_colnames=True,
            low_memory=True  # Enable memory optimization
        )
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
    except MemoryError:
        print("Memory error! Try increasing min_support further or reducing dataset size")
        return pd.DataFrame()

def run_association_rules(data, output_rules, output_image, min_sup, min_conf):
    rules = analyze_real_data(
        data=data,
        min_support=min_sup,
        min_confidence=min_conf,
        image=output_image
    )
    if not rules.empty:
        rules.to_csv(output_rules, index=False)
        print(f"Saved {len(rules)} rules to {output_rules}")
'''
def parse_args():
    parser = argparse.ArgumentParser(
        description="Score datasets before and after cleaning based on missingness criteria"
    )
    # Support both positional and optional for input/output
    parser.add_argument('--input_file', help='Alternative input CSV path')
    parser.add_argument('--output_csv', help='Alternative output CSV path')
    parser.add_argument('--important-cols', type=str, default='',
                        help='Comma-separated list of important columns')
    parser.add_argument('--imp-weight', type=float, default=1.0,
                        help='Penalty weight for missing in important columns')
    parser.add_argument('--pct-thresh', type=float, default=0.0,
                        help='Percentile threshold for row missingness (0-1)')
    parser.add_argument('--min-rows', type=int, default=0,
                        help='Minimum rows to keep')
    parser.add_argument('--min-pct', type=float, default=0.0,
                        help='Minimum percentage of rows to keep (0-1)')
    parser.add_argument('--max-col-missing-pct', type=float, default=1.0,
                        help='Max missing percentage allowed per column (0-1)')
    parser.add_argument('--min-cols', type=int, default=0,
                        help='Minimum columns to keep')
    #parser.add_argument('--min_support', type=float, default=0.1,
    #                    help='Minimum support threshold (default: 0.1)')
    #parser.add_argument('--min_confidence', type=float, default=0.5,
    #                    help='Minimum confidence threshold (default: 0.5)')
    
    args = parser.parse_args()
    
    if not args.input_file or not args.output_csv:
        parser.error("Both input and output CSV paths must be provided.")

    return args

def score_dataset(df: pd.DataFrame, cfg: dict, orig_shape: tuple) -> dict:
    rows, cols = df.shape
    orig_rows, orig_cols = orig_shape

    total_na = df.isna().sum().sum()
    rel_na = total_na / (orig_rows * orig_cols)

    # Row-wise
    na_mask = df.isna()
    row_scores = na_mask.sum(axis=1).astype(float)
    if cfg['important_cols']:
        row_scores += na_mask[cfg['important_cols']].sum(axis=1) * (cfg['imp_weight'] - 1)
    max_row_score = row_scores.max() if rows > 0 else 0.0
    row_score_threshold = row_scores.quantile(1 - cfg['pct_thresh']) if rows > 0 else 0.0

    # Column-wise
    col_na_pct = df.isna().mean()
    max_col_na = col_na_pct.max() if cols > 0 else 0.0

    # Retention
    pct_rows_kept = rows / orig_rows
    pct_cols_kept = cols / orig_cols

    # Check constraints
    feasibility = (
        rows >= cfg['min_rows'] and
        pct_rows_kept >= cfg['min_pct'] and
        cols >= cfg['min_cols'] and
        max_col_na <= cfg['max_col_missing_pct'] and
        max_row_score <= row_score_threshold
    )

    return {
        'total_na': total_na,
        'rel_na': rel_na,
        'max_row_score': max_row_score,
        'row_score_threshold': row_score_threshold,
        'max_col_na': max_col_na,
        'rows_kept': rows,
        'cols_kept': cols,
        'pct_rows_kept': pct_rows_kept,
        'pct_cols_kept': pct_cols_kept,
        'feasible': feasibility
    }

def compute_health_score(metrics: dict, cfg: dict) -> float:
    rel_na = metrics['rel_na']           # 0..1
    pct_rows = metrics['pct_rows_kept']    # 0..1
    pct_cols = metrics['pct_cols_kept']    # 0..1
    max_row = metrics['max_row_score']    # absolute count
    tau_r = metrics['row_score_threshold']
    max_col = metrics['max_col_na']       # fraction
    tau_c = cfg['max_col_missing_pct']  # fraction

    # normalize sub‑scores
    s1 = 1 - rel_na
    s2 = pct_rows
    s3 = pct_cols
    s4 = 1 - min(max_row / tau_r if tau_r > 0 else 0, 1)
    s5 = 1 - min(max_col / tau_c if tau_c > 0 else 0, 1)

    # weights (must sum to 1)
    w1, w2, w3, w4, w5 = 0.35, 0.10, 0.10, 0.25, 0.20

    # final score
    return w1*s1 + w2*s2 + w3*s3 + w4*s4 + w5*s5




def main():
    args = parse_args()
    
    # Load datasets once
    print("\nLoading datasets...")
    df_input = pd.read_csv(args.input_file)
    df_output = pd.read_csv(args.output_csv)
    
    # Score datasets
    cfg = {
        'important_cols': [c.strip() for c in args.important_cols.split(',') if c.strip()],
        'imp_weight': args.imp_weight,
        'pct_thresh': args.pct_thresh,
        'min_rows': args.min_rows,
        'min_pct': args.min_pct,
        'max_col_missing_pct': args.max_col_missing_pct,
        'min_cols': args.min_cols
    }
    
    print("\n== Input Dataset Metrics ==")
    input_metrics = score_dataset(df_input, cfg, df_input.shape)
    print_metrics(input_metrics)
    
    print("\n== Output Dataset Metrics ==")
    output_metrics = score_dataset(df_output, cfg, df_input.shape)
    print_metrics(output_metrics)
    
    '''
    # Process association rules using pre-loaded data
    print("\nAnalyzing input dataset rules...")
    run_association_rules(
        data=df_input,
        output_rules='rules_before.csv',
        output_image='rules_before.png',
        min_sup=args.min_support,
        min_conf=args.min_confidence
    )
    
    print("\nAnalyzing output dataset rules...")
    run_association_rules(
        data=df_output,
        output_rules='rules_after.csv',
        output_image='rules_after.png',
        min_sup=args.min_support,
        min_conf=args.min_confidence
    )
    '''
    
    # Calculate final scores
    input_score = compute_health_score(input_metrics, cfg)
    output_score = compute_health_score(output_metrics, cfg)
    print(f"\nFinal Scores:")
    print(f"Input health:  {input_score:.3f}")
    print(f"Output health: {output_score:.3f}")

def print_metrics(metrics):
    for k, v in metrics.items():
        print(f"{k:>20}: {v:.4f}" if isinstance(v, float) else f"{k:>20}: {v}")

main()