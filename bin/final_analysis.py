import pandas as pd
import argparse

def calculate_score(original_path, cleaned_path, constraints):
    """Calculate and print the quality score for a cleaned dataset."""
    # Read datasets
    original = pd.read_csv(original_path)
    cleaned = pd.read_csv(cleaned_path)
    
    # Base metrics
    orig_rows = len(original)
    orig_cols = len(original.columns)
    orig_missing = original.isna().sum().sum()
    
    cleaned_rows = len(cleaned)
    cleaned_cols = len(cleaned.columns)
    cleaned_missing = cleaned.isna().sum().sum()
    
    # Important columns metrics
    important_cols = [col.strip() for col in constraints['important_cols'].split(',') if col.strip()]
    orig_imp_missing = original[important_cols].isna().sum().sum() if important_cols else 0
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
        percent_kept = (cleaned_rows / orig_rows) * 100
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
        percent_cols = (cleaned_cols / orig_cols) * 100
        met_constraints += 1 if percent_cols >= constraints['col_relative_threshold'] else 0
        
    constraint_score = (met_constraints / total_constraints * 40) if total_constraints > 0 else 40.0

    # 2. Missing Value Reduction Score (30%)
    if orig_missing == 0:
        missing_score = 30.0 if cleaned_missing == 0 else 0.0
    else:
        missing_reduction = 1 - (cleaned_missing / orig_missing)
        missing_score = max(0.0, missing_reduction * 30)

    # 3. Data Retention Score (20%)
    row_retention = cleaned_rows / orig_rows
    col_retention = cleaned_cols / orig_cols
    retention_score = (row_retention + col_retention) * 10  # Max 20
    
    # Penalize if column retention drops below 80%
    if col_retention < 0.8:
        retention_score -= 5

    # 4. Important Columns Bonus (10%)
    if not important_cols or orig_imp_missing == 0:
        important_bonus = 0.0
    else:
        imp_reduction = 1 - (cleaned_imp_missing / orig_imp_missing)
        important_bonus = min(imp_reduction * 10, 10.0)
        # Bonus multiplier for >30% reduction
        if imp_reduction > 0.3:
            important_bonus *= 1.2

    total_score = constraint_score + missing_score + retention_score + min(important_bonus, 10.0)

    # Print metrics
    print(f"\n{' DATASET METRICS ':=^40}")
    print(f"Original: {orig_rows} rows, {orig_cols} columns")
    print(f"Cleaned: {cleaned_rows} rows, {cleaned_cols} columns")
    print(f"\nMissing Values:")
    print(f"Original: {orig_missing}")
    print(f"Cleaned: {cleaned_missing} (Reduction: {orig_missing - cleaned_missing})")
    
    if important_cols:
        print(f"\nImportant Columns ({', '.join(important_cols)}):")
        print(f"Original Missing: {orig_imp_missing}")
        print(f"Cleaned Missing: {cleaned_imp_missing} (Reduction: {orig_imp_missing - cleaned_imp_missing})")
    
    print(f"\nRetention Rates:")
    print(f"Rows: {row_retention:.1%}")
    print(f"Columns: {col_retention:.1%}{' (Penalty Applied)' if col_retention < 0.8 else ''}")

    # Print scores
    print(f"\n{' SCORE BREAKDOWN ':=^40}")
    print(f"Constraint Adherence: {constraint_score:.1f}/40")
    print(f"Missing Value Reduction: {missing_score:.1f}/30")
    print(f"Data Retention: {retention_score:.1f}/20")
    print(f"Important Columns Bonus: {min(important_bonus, 10.0):.1f}/10")
    print(f"{' TOTAL SCORE ':=^40}")
    print(f"{total_score:.1f}/100\n")
    
    return total_score

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate cleaning score for a single dataset')
    parser.add_argument('--original', required=True, help='Original dataset path')
    parser.add_argument('--cleaned', required=True, help='Cleaned dataset path')
    parser.add_argument('--min-rows', type=int, default=0, help='Minimum rows requirement')
    parser.add_argument('--min-percent', type=float, default=0.0, help='Minimum %% rows to keep')
    parser.add_argument('--max-missing', type=int, default=0, help='Maximum allowed missing values')
    parser.add_argument('--col-threshold', type=int, default=0, help='Minimum columns to keep')
    parser.add_argument('--col-relative-threshold', type=float, default=0.0, help='Minimum %% of columns to keep (0-100)')
    parser.add_argument('--important-cols', default='', help='Comma-separated important columns')
    
    args = parser.parse_args()
    
    calculate_score(
        original_path=args.original,
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