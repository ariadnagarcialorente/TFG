import argparse
import pandas as pd
import os
import numpy as np

def compute_weighted_missing(data, important_cols, weight):
    """Compute weighted missing values with priority to important columns"""
    if important_cols and weight > 1.0:
        imp_cols = [col for col in important_cols if col in data.columns]
        other_cols = [col for col in data.columns if col not in imp_cols]
        imp_na = data[imp_cols].isna().sum(axis=1)
        oth_na = data[other_cols].isna().sum(axis=1)
        return imp_na * weight + oth_na
    return data.isna().sum(axis=1)

def main():
    parser = argparse.ArgumentParser(description='Constraint-driven data cleaning with row prioritization')
    parser.add_argument('--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('--output', type=str, required=True, help='Output CSV file')
    parser.add_argument('-c','--important-cols', default='', help='Comma-separated important columns')
    parser.add_argument('-w','--importance-weight', type=float, default=2.0)
    parser.add_argument('-r','--min-rows', type=int, default=0)
    parser.add_argument('-m','--max-missing', type=int, default=0)
    parser.add_argument('-mp','--min-percent', type=float, default=0.0)
    parser.add_argument('-ct','--col-threshold', type=int, default=0)
    parser.add_argument('-crt','--col-relative-threshold', type=float, default=0.0)
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    # Load data
    data = pd.read_csv(args.input)
    important_cols = [c.strip() for c in args.important_cols.split(',') if c.strip()]
    
    # Calculate minimum constraints
    min_rows_required = max(
        args.min_rows, 
        int(len(data) * args.min_percent / 100)
    )
    min_cols_required = max(
        args.col_threshold, 
        int(len(data.columns) * args.col_relative_threshold / 100)
    )
    
    current = data.copy()
    current_missing = current.isna().sum().sum()
    important_cols_set = set(important_cols)
    
    # Store original dimensions for reporting
    original_rows, original_cols = current.shape
    print(f'Starting cleaning: {original_rows} rows, {original_cols} cols, {current_missing} missing')
    print(f'Constraints: min_rows={min_rows_required}, max_missing={args.max_missing}, min_cols={min_cols_required}')
    
    # Phase 1: Remove high-missing columns first
    if current_missing > args.max_missing and len(current.columns) > min_cols_required:
        removable_cols = [col for col in current.columns if col not in important_cols_set]
        if removable_cols:
            col_missing = current[removable_cols].isna().sum()
            # Sort columns by missing count (descending)
            sorted_cols = col_missing.sort_values(ascending=False)
            
            for col in sorted_cols.index:
                if len(current.columns) <= min_cols_required:
                    break
                    
                col_missing_count = sorted_cols[col]
                if current_missing - col_missing_count <= args.max_missing:
                    # Stop if removing this column would satisfy constraint
                    break
                    
                current = current.drop(columns=[col])
                current_missing -= col_missing_count
                if args.verbose:
                    print(f'Removed col {col} ({col_missing_count} missing)')
                
                if current_missing <= args.max_missing:
                    break

    # Phase 2: Remove rows until constraints are met
    iteration = 0
    while current_missing > args.max_missing and len(current) > min_rows_required:
        iteration += 1
        if iteration > 10000:  # Increased safety limit
            print("Max iterations reached in row removal")
            break
            
        row_weights = compute_weighted_missing(current, important_cols, args.importance_weight)
        worst_row = row_weights.idxmax()
        row_missing_count = current.loc[worst_row].isna().sum()
        
        current = current.drop(index=[worst_row])
        current_missing -= row_missing_count
        
        if args.verbose:
            print(f'Iter {iteration}: Removed row {worst_row} ({row_missing_count} missing)')

    # Final constraint check
    current_rows = len(current)
    current_cols = len(current.columns)
    current_percent = (current_rows / original_rows) * 100
    
    constraints_met = (
        current_missing <= args.max_missing and
        current_rows <= min_rows_required and  # Should be >=
        current_percent <= args.min_percent    # Should be >=
    )
    
    # Save results
    print(f'Finished: {current_rows} rows, {current_cols} cols, {current_missing} missing')
    print(f'Rows retained: {current_rows}/{original_rows} ({current_percent:.1f}%)')
    print(f'Constraints: {"MET" if constraints_met else "NOT MET"}')
    
    current.to_csv(args.output, index=False)
    print(f'Saved to {os.path.abspath(args.output)}')

if __name__ == '__main__':
    main()