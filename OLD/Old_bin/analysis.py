import argparse
import pandas as pd


def get_user_inputs(df: pd.DataFrame) -> dict:
    print("Dataset shape:", df.shape)
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
    rows, cols = df.shape
    orig_rows, orig_cols = orig_shape

    total_na = df.isna().sum().sum()
    rel_na = total_na / (orig_rows * orig_cols)

    na_mask = df.isna()
    row_scores = na_mask.sum(axis=1).astype(float)
    if cfg['important_cols']:
        row_scores += na_mask[cfg['important_cols']].sum(axis=1) * (cfg['imp_weight'] - 1)
    max_row_score = row_scores.max() if rows > 0 else 0.0
    row_score_threshold = row_scores.quantile(1 - cfg['pct_thresh']) if rows > 0 else 0.0

    col_na_pct = df.isna().mean()
    max_col_na = col_na_pct.max() if cols > 0 else 0.0

    pct_rows_kept = rows / orig_rows
    pct_cols_kept = cols / orig_cols

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
    """
    Given the output of `score_dataset` (metrics)
    and the user cfg (to get row/col thresholds),
    returns a single health score in [0,1].
    """
    # unpack
    rel_na   = metrics['rel_na']           # 0..1
    pct_rows = metrics['pct_rows_kept']    # 0..1
    pct_cols = metrics['pct_cols_kept']    # 0..1
    max_row  = metrics['max_row_score']    # absolute count
    tau_r    = metrics['row_score_threshold']
    max_col  = metrics['max_col_na']       # fraction
    tau_c    = cfg['max_col_missing_pct']  # fraction

    # normalize sub‑scores
    s1 = 1 - rel_na
    s2 = pct_rows
    s3 = pct_cols
    s4 = 1 - min(max_row / tau_r if tau_r>0 else 0, 1)
    s5 = 1 - min(max_col / tau_c if tau_c>0 else 0, 1)

    # weights (must sum to 1)
    w1, w2, w3, w4, w5 = 0.25, 0.20, 0.20, 0.20, 0.15

    # final score
    return w1*s1 + w2*s2 + w3*s3 + w4*s4 + w5*s5

def main():
    parser = argparse.ArgumentParser(description="Score input and output datasets based on NA distribution and user constraints")
    parser.add_argument('input_csv', help='Original dataset CSV')
    parser.add_argument('output_csv', help='Cleaned dataset CSV')
    args = parser.parse_args()

    df_input = pd.read_csv(args.input_csv)
    df_output = pd.read_csv(args.output_csv)

    cfg = get_user_inputs(df_input)
    orig_shape = df_input.shape

    print("\n== Input Dataset Score ==")
    input_score = score_dataset(df_input, cfg, orig_shape)
    for k, v in input_score.items():
        print(f"{k}: {v}")

    print("\n== Output Dataset Score ==")
    output_score = score_dataset(df_output, cfg, orig_shape)
    for k, v in output_score.items():
        print(f"{k}: {v}")

    # after computing 'input_metrics' and 'output_metrics':
    input_score  = compute_health_score(input_score, cfg)
    output_score = compute_health_score(output_score, cfg)
    print(f"Input health:  {input_score:.3f}")
    print(f"Output health: {output_score:.3f}")


if __name__ == '__main__':
    main()