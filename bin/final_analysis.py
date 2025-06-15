import pandas as pd
from pandas.errors import EmptyDataError
import argparse

def calculate_score(erased_path, cleaned_path, constraints):
    """Calculate and print the quality score for a cleaned dataset."""
    # 1) Load datasets
    erased = pd.read_csv(erased_path)
    try:
        cleaned = pd.read_csv(cleaned_path)
    except EmptyDataError:
        cleaned = pd.DataFrame()

    erased_rows, erased_cols = erased.shape
    cleaned_rows, cleaned_cols = cleaned.shape
    erased_missing = erased.isna().sum().sum()
    raw_cleaned_missing = cleaned.isna().sum().sum()

    # 2) Important-column missing counts + detect dropped
    important_cols = [c.strip() for c in constraints['important_cols'].split(',') if c.strip()]
    erased_imp_missing = 0
    cleaned_imp_missing = 0
    dropped_imp = []

    for col in important_cols:
        if col in erased.columns:
            erased_imp_missing += erased[col].isna().sum()
        if col in cleaned.columns:
            cleaned_imp_missing += cleaned[col].isna().sum()
        else:
            # Column dropped ⇒ penalize as erased_rows NAs
            dropped_imp.append(col)
            cleaned_imp_missing += erased_rows

    # 3) Include drop-penalties in overall missing count
    cleaned_missing = raw_cleaned_missing + cleaned_imp_missing

    if dropped_imp:
        print(f"Warning: Important columns dropped (penalized as missing): {', '.join(dropped_imp)}")

    # 4) Constraint Adherence Score (40%)
    met = total = 0
    # Min rows
    if constraints['min_rows'] > 0:
        total += 1
        if cleaned_rows >= constraints['min_rows']:
            met += 1
    # Min percent rows
    if constraints['min_percent'] > 0:
        total += 1
        if (cleaned_rows / erased_rows) * 100 >= constraints['min_percent']:
            met += 1
    # Max missing
    if constraints['max_missing'] > 0:
        total += 1
        if cleaned_missing <= constraints['max_missing']:
            met += 1
    # Min cols
    if constraints['col_threshold'] > 0:
        total += 1
        if cleaned_cols >= constraints['col_threshold']:
            met += 1
    # Min percent cols
    if constraints['col_relative_threshold'] > 0:
        total += 1
        if (cleaned_cols / erased_cols) * 100 >= constraints['col_relative_threshold']:
            met += 1

    constraint_score = (met / total * 40.0) if total > 0 else 40.0

    # 5) Missing Value Reduction Score (30%)
    if erased_missing == 0:
        missing_score = 30.0
    else:
        reduction = (erased_missing - cleaned_missing) / erased_missing
        missing_score = max(0.0, min(30.0, reduction * 30.0))

    # 6) Data Retention Score (20%)
    row_ret = cleaned_rows / erased_rows
    col_ret = cleaned_cols / erased_cols
    retention_score = (row_ret + col_ret) * 10.0

    # 7) Important Columns Bonus (10%)
    if dropped_imp:
        bonus = 0.0
    elif not important_cols or erased_imp_missing == 0:
        bonus = 10.0
    else:
        imp_red = (erased_imp_missing - cleaned_imp_missing) / erased_imp_missing
        bonus = max(0.0, min(10.0, imp_red * 10.0))

    # 8) Total Score
    total_score = max(constraint_score + missing_score + retention_score + bonus, 0)

    # Print metrics
    print(f"\n{' DATASET METRICS ':=^50}")
    print(f"Erased: {erased_rows} rows, {erased_cols} columns, {erased_missing} missing")
    print(f"Cleaned: {cleaned_rows} rows, {cleaned_cols} columns, {cleaned_missing} missing")

    if important_cols:
        print(f"\nImportant Columns ({', '.join(important_cols)}):")
        print(f"  Erased Missing: {erased_imp_missing}")
        print(f"  Cleaned Missing (including penalized drops): {cleaned_imp_missing}")
        if erased_imp_missing > 0:
            red = erased_imp_missing - cleaned_imp_missing
            pct = (red / erased_imp_missing) * 100
            print(f"  Reduction: {red} ({pct:.1f}%)")

    print(f"\nRetention Rates:")
    print(f"  Rows: {row_ret:.1%}")
    print(f"  Columns: {col_ret:.1%}{' (Penalty Applied)' if col_ret < 0.5 else ''}")

    print(f"\n{' SCORE BREAKDOWN ':=^50}")
    print(f"Constraint Adherence: {constraint_score:.1f}/40")
    print(f"Missing Value Reduction: {missing_score:.1f}/30")
    print(f"Data Retention: {retention_score:.1f}/20")
    print(f"Important Columns Bonus: {bonus:.1f}/10")
    print(f"{' TOTAL SCORE ':=^50}")
    print(f"{total_score:.1f}/100\n")

    return total_score

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate cleaning score for a dataset')
    parser.add_argument('--erased', required=True, help='Path to erased dataset')
    parser.add_argument('--cleaned', required=True, help='Path to cleaned dataset')
    parser.add_argument('--min-rows', type=int, default=0, help='Minimum number of rows')
    parser.add_argument('--min-percent', type=float, default=0.0, help='Minimum % of rows to keep')
    parser.add_argument('--max-missing', type=int, default=0, help='Max allowed missing values')
    parser.add_argument('--col-threshold', type=int, default=0, help='Minimum number of columns to keep')
    parser.add_argument('--col-relative-threshold', type=float, default=0.0, help='Minimum % of columns to keep')
    parser.add_argument('--important-cols', default='', help='Comma-separated list of important columns')
    args = parser.parse_args()

    calculate_score(
        erased_path=args.erased,
        cleaned_path=args.cleaned,
        constraints={
            'min_rows': args.min_rows,
            'min_percent': args.min_percent,
            'max_missing': args.max_missing,
            'col_threshold': args.col_threshold,
            'col_relative_threshold': args.col_relative_threshold,
            'important_cols': args.important_cols
        }
    )
