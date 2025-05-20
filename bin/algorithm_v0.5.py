import pandas as pd


def get_user_inputs(df: pd.DataFrame):
    """
    Prompt user for filtering criteria and return config.
    """
    print("Dataset shape:", df.shape)
    print("Available columns:", list(df.columns))
    important = input("Enter important columns (comma-separated), or leave blank: ")
    important_cols = [c.strip() for c in important.split(',') if c.strip()] if important else []
    imp_weight = 1.0
    if important_cols:
        imp_weight = float(input("Enter penalty weight for missing in important columns (e.g. 2.0): "))

    # Row thresholds
    pct_thresh = float(input("Percentile threshold for row missingness (0-100): ")) / 100
    min_rows = int(input("Minimum rows to keep: "))
    min_pct = float(input("Minimum percentage of rows to keep (0-100): ")) / 100

    # Column thresholds
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
    """
    Compute missingness score per row, with extra weight for important cols.
    """
    na = df.isna()
    base = na.sum(axis=1).astype(float)
    if cfg['important_cols']:
        imp_missing = na[cfg['important_cols']].sum(axis=1)
        base += imp_missing * (cfg['imp_weight'] - 1)
    return base


def compute_col_scores(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """
    Compute missingness score per column (percentage missing).
    """
    return df.isna().mean()


def criteria_met(df: pd.DataFrame, cfg: dict) -> bool:
    """
    Check whether current df meets user thresholds.
    """
    rows, cols = df.shape
    row_pct = rows / orig_shape[0]

    # row missing: max score <= percentile threshold
    scores = compute_row_scores(df, cfg)
    max_score = scores.quantile(1.0 - cfg['pct_thresh'])

    # column missing: max missing pct per col <= threshold
    col_scores = compute_col_scores(df, cfg)
    max_col = col_scores.max()

    return (
        rows >= cfg['min_rows'] and
        row_pct >= cfg['min_pct'] and
        max_score <= scores.quantile(cfg['pct_thresh']) and
        cols >= cfg['min_cols'] and
        max_col <= cfg['max_col_missing_pct']
    )


def iterative_clean(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """
    Iteratively drop the row or column with highest score until criteria are met.
    """
    iteration = 0
    while True:
        iteration += 1
        row_scores = compute_row_scores(df, cfg)
        col_scores = compute_col_scores(df, cfg)

        # identify worst offenders
        worst_row_idx = row_scores.idxmax()
        worst_row_score = row_scores.max()
        worst_col = col_scores.idxmax()
        worst_col_score = col_scores.max()

        print(f"Iteration {iteration}: worst row {worst_row_idx} (score={worst_row_score:.2f}),"
              f" worst col '{worst_col}' (pct={worst_col_score:.2%})")

        # decide removal
        if worst_row_score >= worst_col_score * df.shape[0]:
            print(f"Dropping row {worst_row_idx}")
            df = df.drop(index=worst_row_idx)
        else:
            print(f"Dropping column '{worst_col}'")
            df = df.drop(columns=[worst_col])

        # reindex rows after drop
        df = df.reset_index(drop=True)

        # check stop condition
        if criteria_met(df, cfg):
            print("All criteria satisfied. Stopping.")
            break

    return df


df = pd.read_csv('output_erased_dataset.csv')
global orig_shape
orig_shape = df.shape

cfg = get_user_inputs(df)

cleaned = iterative_clean(df, cfg)
cleaned.to_csv('cleaned_dataset.csv', index=False)
print(f"Cleaned dataset saved with shape: {cleaned.shape}")

