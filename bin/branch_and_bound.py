import pandas as pd


def get_user_inputs(df: pd.DataFrame):
    print("Dataset shape:", df.shape)
    print("Available columns:", list(df.columns))
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

def compute_row_scores(df: pd.DataFrame, cfg: dict) -> pd.Series:
    na = df.isna()
    base = na.sum(axis=1).astype(float)
    if cfg['important_cols']:
        imp_missing = na[cfg['important_cols']].sum(axis=1)
        base += imp_missing * (cfg['imp_weight'] - 1)
    return base

def compute_col_scores(df: pd.DataFrame) -> pd.Series:
    return df.isna().mean()

def is_feasible(df: pd.DataFrame, cfg: dict) -> bool:
    if df.shape[0] < cfg['min_rows'] or df.shape[1] < cfg['min_cols']:
        return False
    if df.shape[0] / cfg['orig_rows'] < cfg['min_pct']:
        return False
    if df.isna().mean().max() > cfg['max_col_missing_pct']:
        return False
    row_scores = compute_row_scores(df, cfg)
    if row_scores.quantile(cfg['pct_thresh']) > cfg['row_score_threshold']:
        return False
    return True

def branch_and_bound(df, cfg):
    cfg['orig_rows'] = df.shape[0]
    row_scores = compute_row_scores(df, cfg)
    cfg['row_score_threshold'] = row_scores.quantile(cfg['pct_thresh'])
    best = {'df': None, 'cost': float('inf')}

    def recurse(remaining_df, dropped_rows, dropped_cols):
        if len(dropped_rows) + len(dropped_cols) >= best['cost']:
            return

        if is_feasible(remaining_df, cfg):
            cost = len(dropped_rows) + len(dropped_cols)
            if cost < best['cost']:
                best.update({'df': remaining_df.copy(), 'cost': cost})
            return

        row_scores = compute_row_scores(remaining_df, cfg)
        col_scores = compute_col_scores(remaining_df)
        if not row_scores.empty:
            worst_row = row_scores.idxmax()
            recurse(remaining_df.drop(index=worst_row).reset_index(drop=True), dropped_rows | {worst_row}, dropped_cols)
        if not col_scores.empty:
            worst_col = col_scores.idxmax()
            recurse(remaining_df.drop(columns=[worst_col]), dropped_rows, dropped_cols | {worst_col})

    recurse(df, set(), set())
    return best['df'], best['cost']


df = pd.read_csv('output_erased_dataset.csv')
cfg = get_user_inputs(df)
cleaned_df, cost = branch_and_bound(df, cfg)

if cleaned_df is not None:
    cleaned_df.to_csv('cleaned_dataset.csv', index=False)
    print(f"\nOptimization complete. Rows/columns removed: {cost}")
    print(f"Final shape: {cleaned_df.shape}")
else:
    print("No feasible solution found under current constraints.")

