import argparse
import pandas as pd
import os
import numpy as np
from pandas.util import hash_pandas_object

def normalize(series):
    min_val = series.min()
    max_val = series.max()
    return (series - min_val) / (max_val - min_val) if max_val != min_val else pd.Series(0.5, index=series.index)

def calculate_dataset_score(data, important_cols, importance_weight):
    if data.empty or data.shape[1] == 0:
        return float('inf'), pd.Series(dtype=float)
    other_cols = [c for c in data.columns if c not in important_cols]
    if important_cols and importance_weight > 1.0:
        imp_na = data[important_cols].isna().sum(axis=1)
        oth_na = data[other_cols].isna().sum(axis=1)
        na_weighted = imp_na * importance_weight + oth_na
    else:
        na_weighted = data.isna().sum(axis=1)
    sorted_idx = na_weighted.argsort()[::-1]
    ranks = np.empty_like(sorted_idx)
    ranks[sorted_idx] = np.arange(len(sorted_idx))
    norm_missing = normalize(na_weighted)
    norm_rank = normalize(pd.Series(ranks, index=data.index))
    combined = norm_missing + norm_rank
    return combined.mean(), combined

def analyze_missing_patterns_optimized(data, top_n=10):
    """Optimized pattern analysis using vectorized hashing."""
    na_mask = data.isna()
    hashes = hash_pandas_object(na_mask, index=False).astype('int64')
    pattern_counts = hashes.value_counts().head(top_n)
    return hashes.isin(pattern_counts.index)

def main():
    parser = argparse.ArgumentParser(description='Optimized data cleaning')
    parser.add_argument('--input', type=str, default='output_erased_dataset.csv')
    parser.add_argument('--output', type=str, default='cleaned_dataset.csv')
    parser.add_argument('-c','--important-cols', default='')
    parser.add_argument('-w','--importance-weight', type=float, default=1.0)
    parser.add_argument('-r','--min-rows', type=int, default=0)
    parser.add_argument('-m','--max-missing', type=int, default=0)
    parser.add_argument('-mp','--min-percent', type=float, default=0.0)
    parser.add_argument('-ct','--col-threshold', type=int, default=0)
    parser.add_argument('-crt','--col-relative-threshold', type=float, default=0.0)
    parser.add_argument('-tp','--top-patterns', type=int, default=10)
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    print('Loading data...')
    data = pd.read_csv(args.input)
    important_cols = [c.strip() for c in args.important_cols.split(',') if c.strip()]
    orig_rows, orig_cols = data.shape
    min_cols = max(args.col_threshold, int(orig_cols * args.col_relative_threshold / 100))
    min_rows = max(args.min_rows, int(orig_rows * args.min_percent / 100))

    current = data.copy()
    curr_imp = [c for c in important_cols if c in current.columns]
    curr_score, row_scores = calculate_dataset_score(current, curr_imp, args.importance_weight)
    print(f'Initial dims: {orig_rows} rows, {orig_cols} columns | score: {curr_score:.4f}')
    
    iteration = 0
    while True:
        iteration += 1
        best_score, best_type, best_id = curr_score, None, None
        if current.shape[1] > min_cols:
            na_counts = current[[c for c in current.columns if c not in curr_imp]].isna().sum()
            worst_col = na_counts.idxmax()
            temp = current.drop(columns=[worst_col])
            temp_imp = [c for c in curr_imp if c != worst_col]
            sc, _ = calculate_dataset_score(temp, temp_imp, args.importance_weight)
            if sc < best_score:
                best_score, best_type, best_id = sc, 'col', worst_col
        if current.shape[0] > min_rows:
            worst_row = row_scores.idxmax()
            temp = current.drop(index=[worst_row])
            sc, temp_rs = calculate_dataset_score(temp, curr_imp, args.importance_weight)
            if sc < best_score:
                best_score, best_type, best_id = sc, 'row', worst_row
                best_row_scores = temp_rs
        if args.max_missing > 0 and current.isna().sum().sum() > args.max_missing:
            best_type, best_id = 'row', row_scores.idxmax()
            sc, best_row_scores = calculate_dataset_score(current.drop(index=[best_id]), curr_imp, args.importance_weight)
            best_score = sc
        if best_type is None:
            if args.verbose: print('No further improvement.')
            break
        if best_type == 'col':
            print(f"Iteration {iteration}: Remove column '{best_id}' -> score {best_score:.4f}")
            current = current.drop(columns=[best_id])
            curr_imp = [c for c in curr_imp if c != best_id]
        else:
            print(f"Iteration {iteration}: Remove row {best_id} -> score {best_score:.4f}")
            current = current.drop(index=[best_id])
            row_scores = best_row_scores
        curr_score = best_score

    print('\nApplying optimized pattern filter...')
    mask = analyze_missing_patterns_optimized(current, args.top_patterns)
    result = current[mask]
    print(f'Retained {len(result)}/{len(current)} rows matching top {args.top_patterns} patterns')

    result.to_csv(args.output, index=False)
    print(f'Final dims: {result.shape[0]} rows, {result.shape[1]} columns saved to {os.path.abspath(args.output)}')

if __name__ == '__main__':
    main()