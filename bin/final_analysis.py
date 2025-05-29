import pandas as pd
import argparse

def calculate_score(complete_path, erased_path, cleaned_path, constraints):
    """Calculate and print the quality score for a cleaned dataset."""
    # Read datasets
    complete = pd.read_csv(complete_path)
    erased = pd.read_csv(erased_path)
    cleaned = pd.read_csv(cleaned_path)
    
    # Base metrics
    complete_rows = len(complete)
    complete_cols = len(complete.columns)
    
    erased_rows = len(erased)
    erased_cols = len(erased.columns)
    erased_missing = erased.isna().sum().sum()
    
    cleaned_rows = len(cleaned)
    cleaned_cols = len(cleaned.columns)
    cleaned_missing = cleaned.isna().sum().sum()
    
    # Important columns metrics
    important_cols = [col.strip() for col in constraints['important_cols'].split(',') if col.strip()]
    erased_imp_missing = erased[important_cols].isna().sum().sum() if important_cols else 0
    cleaned_imp_missing = cleaned[important_cols].isna().sum().sum() if important_cols else 0

    # 1. Constraint Adherence Score (40%)
    met_constraints = 0
    total_constraints = 0
    
    # Check row constraints
    if constraints['min_rows'] > 0:
        total_constraints += 1
        met_constraints += 1 if cleaned_rows >= constraints['min_rows'] else 0
        
    if constraints['min_percent'] > 0:
        total_constraints += 1
        percent_kept = (cleaned_rows / complete_rows) * 100
        met_constraints += 1 if percent_kept >= constraints['min_percent'] else 0
        
    if constraints['max_missing'] > 0:
        total_constraints += 1
        met_constraints += 1 if cleaned_missing <= constraints['max_missing'] else 0
    
    # Check column constraints
    if constraints['col_threshold'] > 0:
        total_constraints += 1
        met_constraints += 1 if cleaned_cols >= constraints['col_threshold'] else 0
        
    if constraints['col_relative_threshold'] > 0:
        total_constraints += 1
        percent_cols = (cleaned_cols / complete_cols) * 100
        met_constraints += 1 if percent_cols >= constraints['col_relative_threshold'] else 0
        
    constraint_score = (met_constraints / total_constraints * 40) if total_constraints > 0 else 40.0

    # 2. Missing Value Reduction Score (30%)
    if erased_missing == 0:
        missing_score = 30.0  # Full points if no missing to begin with
    else:
        missing_reduction = (erased_missing - cleaned_missing) / erased_missing
        missing_score = max(0.0, min(30.0, missing_reduction * 30))

    # 3. Data Retention Score (20%)
    row_retention = cleaned_rows / complete_rows
    col_retention = cleaned_cols / complete_cols
    retention_score = (row_retention + col_retention) * 10  # Max 20
    
    # Penalize only if column retention drops below 50%
    if col_retention < 0.5:
        retention_score -= 5

    # 4. Important Columns Bonus (10%)
    if not important_cols or erased_imp_missing == 0:
        important_bonus = 10.0
    else:
        imp_reduction = (erased_imp_missing - cleaned_imp_missing) / erased_imp_missing
        important_bonus = min(10.0, imp_reduction * 10)

    total_score = constraint_score + missing_score + retention_score + important_bonus

    # Print metrics
    print(f"\n{' DATASET METRICS ':=^40}")
    print(f"Complete: {complete_rows} rows, {complete_cols} columns")
    print(f"Erased: {erased_rows} rows, {erased_cols} columns, {erased_missing} missing")
    print(f"Cleaned: {cleaned_rows} rows, {cleaned_cols} columns, {cleaned_missing} missing")
    
    if important_cols:
        print(f"\nImportant Columns ({', '.join(important_cols)}):")
        print(f"Erased Missing: {erased_imp_missing}")
        print(f"Cleaned Missing: {cleaned_imp_missing}")
        print(f"Reduction: {erased_imp_missing - cleaned_imp_missing} ({((erased_imp_missing - cleaned_imp_missing)/erased_imp_missing*100 if erased_imp_missing > 0 else 0):.1f}%)")
    
    print(f"\nRetention Rates:")
    print(f"Rows: {row_retention:.1%}")
    print(f"Columns: {col_retention:.1%}{' (Penalty Applied)' if col_retention < 0.5 else ''}")

    # Print scores
    print(f"\n{' SCORE BREAKDOWN ':=^40}")
    print(f"Constraint Adherence: {constraint_score:.1f}/40")
    print(f"Missing Value Reduction: {missing_score:.1f}/30")
    print(f"Data Retention: {retention_score:.1f}/20")
    print(f"Important Columns Bonus: {important_bonus:.1f}/10")
    print(f"{' TOTAL SCORE ':=^40}")
    print(f"{total_score:.1f}/100\n")
    
    return total_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate cleaning score for a single dataset')
    parser.add_argument('--complete', required=True, help='Complete dataset path')
    parser.add_argument('--erased', required=True, help='Erased dataset path')
    parser.add_argument('--cleaned', required=True, help='Cleaned dataset path')
    parser.add_argument('--min-rows', type=int, default=0, help='Minimum rows requirement')
    parser.add_argument('--min-percent', type=float, default=0.0, help='Minimum %% rows to keep')
    parser.add_argument('--max-missing', type=int, default=0, help='Maximum allowed missing values')
    parser.add_argument('--col-threshold', type=int, default=0, help='Minimum columns to keep')
    parser.add_argument('--col-relative-threshold', type=float, default=0.0, help='Minimum %% of columns to keep (0-100)')
    parser.add_argument('--important-cols', default='', help='Comma-separated important columns')
    
    args = parser.parse_args()
    
    calculate_score(
        complete_path=args.complete,
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