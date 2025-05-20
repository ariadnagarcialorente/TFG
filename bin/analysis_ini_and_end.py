import argparse
import subprocess
import time
import pandas as pd


def get_user_inputs(df: pd.DataFrame) -> dict:
    """
    Prompt user for scoring criteria.
    """
    print("Initial dataset shape:", df.shape)
    important = input("Enter important columns (comma-separated), or leave blank: ")
    important_cols = [c.strip() for c in important.split(',') if c.strip()] if important else []
    imp_weight = 1.0
    if important_cols:
        imp_weight = float(input("Enter penalty weight for missing in important columns (e.g. 2.0): "))

    pct_thresh = float(input("Percentile threshold for row missingness (0-100): ")) / 100
    min_rows = int(input("Minimum rows to keep: "))
    min_pct = float(input("Minimum percentage of rows to keep (0-100): ")) / 100
    max_col_missing_pct = float(input("Max missing % per column (0-100): ")) / 100
    min_cols = int(input("Minimum columns to keep: "))

    return {
        'important_cols': important_cols,
        'imp_weight': imp_weight,
        'pct_thresh': pct_thresh,
        'min_rows': min_rows,
        'min_pct': min_pct,
        'max_col_missing_pct': max_col_missing_pct,
        'min_cols': min_cols
    }


def score_dataset(df: pd.DataFrame, cfg: dict, orig_shape: tuple) -> dict:
    """
    Compute dataset scores relative to user criteria.
    Returns metrics and feasibility flag.
    """
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


def main():
    parser = argparse.ArgumentParser(
        description="Driver script: score before/after, run algorithm, measure time"
    )
    parser.add_argument('algorithm_file', help='Python script to execute for cleaning')
    parser.add_argument('input_csv', help='Path to original dataset CSV')
    parser.add_argument('output_csv', help='Path where cleaned CSV will be written')
    args = parser.parse_args()

    # Load and score original data
    df_orig = pd.read_csv(args.input_csv)
    cfg = get_user_inputs(df_orig)
    orig_shape = df_orig.shape
    before = score_dataset(df_orig, cfg, orig_shape)
    print("\n== Before Cleaning ==")
    for k, v in before.items():
        print(f"{k}: {v}")

    # Execute algorithm script
    cmd = ['python', args.algorithm_file, args.input_csv, args.output_csv]
    start = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    elapsed = time.time() - start

    if proc.returncode != 0:
        print("\nError running algorithm:")
        print(proc.stdout)
        print(proc.stderr)
        return

    print(f"\nAlgorithm execution time: {elapsed:.3f} seconds")

    # Load and score cleaned data
    df_clean = pd.read_csv(args.output_csv)
    after = score_dataset(df_clean, cfg, orig_shape)
    print("\n== After Cleaning ==")
    for k, v in after.items():
        print(f"{k}: {v}")

if __name__ == '__main__':
    main()
