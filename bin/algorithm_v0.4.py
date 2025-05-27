import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def calculate_dataset_score(data, important_cols, importance_weight):
    """Calculate dataset score with robust percentile-based distribution."""
    if data.empty:
        return float('inf'), pd.Series(dtype=float)
    
    # Non-linear missingness weighting
    if important_cols and importance_weight > 1.0:
        imp_na = data[important_cols].isna().sum(axis=1)
        oth_na = data.drop(columns=important_cols, errors='ignore').isna().sum(axis=1)
        na_weighted = (imp_na ** 2) * importance_weight + oth_na
    else:
        na_weighted = data.isna().sum(axis=1) ** 1.5  # Mild non-linearity
    
    # Percentile-based normalization
    missing_percentile = na_weighted.rank(pct=True)
    
    # Direction-corrected ranking system
    ascending_rank = na_weighted.rank(method='dense', ascending=True)
    rank_percentile = 1 - ascending_rank.rank(pct=True)
    
    # Balanced score composition
    combined = (0.7 * missing_percentile) + (0.3 * rank_percentile)
    combined = pd.Series(combined, index=data.index)
    
    return combined.mean(), combined

def main():
    parser = argparse.ArgumentParser(description='Robust data cleaning via missingness removal')
    parser.add_argument('--input', type=str, default='output_erased_dataset.csv')
    parser.add_argument('--output', type=str, default='cleaned_dataset.csv')
    parser.add_argument('-p','--percentile', type=int, default=75)
    parser.add_argument('-i','--image', type=str, default='missing_distribution.png')
    parser.add_argument('-c','--important-cols', default='')
    parser.add_argument('-w','--importance-weight', type=float, default=1.0)
    parser.add_argument('-r','--min-rows', type=int, default=0)
    parser.add_argument('-m','--max-missing', type=int, default=0)
    parser.add_argument('-mp','--min-percent', type=float, default=0.0)
    parser.add_argument('-ct','--col-threshold', type=int, default=0)
    parser.add_argument('-crt','--col-relative-threshold', type=float, default=0.0)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    print('Loading data...')
    data = pd.read_csv(args.input)
    important_cols = [c.strip() for c in args.important_cols.split(',') if c.strip()]
    original_rows = data.shape[0]
    original_cols = data.shape[1]
    min_cols = max(args.col_threshold, int(original_cols * args.col_relative_threshold))
    min_rows = max(args.min_rows, int(original_rows * args.min_percent / 100))

    current = data.copy()
    current_importants = [c for c in important_cols if c in current.columns]
    current_score, row_scores = calculate_dataset_score(current, current_importants, args.importance_weight)
    print(f'Initial dims: {original_rows} rows, {original_cols} cols | score: {current_score:.4f}')

    iteration = 0
    while True:
        iteration += 1
        if args.verbose:
            print(f'\n--- Iteration {iteration} ---')
        best_col = None
        best_col_score = current_score
        # Column removal evaluation with non-linear penalty
        removable = [c for c in current.columns if c not in current_importants]
        if len(removable) > 0 and current.shape[1] > min_cols:
            col_scores = current[removable].isna().sum() ** 1.2
            worst_col = col_scores.idxmax()
            tmp = current.drop(columns=[worst_col])
            tmp_importants = [c for c in current_importants if c != worst_col]
            score_tmp, _ = calculate_dataset_score(tmp, tmp_importants, args.importance_weight)
            if score_tmp < best_col_score:
                best_col_score = score_tmp
                best_col = worst_col
        # Row removal evaluation
        best_row = None
        best_row_score = current_score
        if current.shape[0] > min_rows:
            worst_row = row_scores.idxmax()
            tmpr = current.drop(index=[worst_row])
            score_r, new_row_scores = calculate_dataset_score(tmpr, current_importants, args.importance_weight)
            if score_r < best_row_score:
                best_row_score = score_r
                best_row = worst_row
        # Greedy removal decision
        if best_col and best_col_score <= best_row_score:
            print(f"Removing column '{best_col}' -> new score {best_col_score:.4f}")
            current = current.drop(columns=[best_col])
            current_importants = [c for c in current_importants if c != best_col]
            current_score, row_scores = calculate_dataset_score(current, current_importants, args.importance_weight)
        elif best_row is not None:
            print(f"Removing row {best_row} -> new score {best_row_score:.4f}")
            current = current.drop(index=[best_row])
            current_score, row_scores = calculate_dataset_score(current, current_importants, args.importance_weight)
        else:
            if args.verbose:
                print('No further improvements.')
            break

    # Final filtering using dynamic threshold
    _, final_scores = calculate_dataset_score(current, current_importants, args.importance_weight)
    thresh = final_scores.quantile(args.percentile/100)
    result = current[final_scores <= thresh]

    result.to_csv(args.output, index=False)
    print(f'Final dims: {result.shape[0]} rows, {result.shape[1]} cols saved to {os.path.abspath(args.output)}')

if __name__ == '__main__':
    main()