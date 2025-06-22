import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

def normalize(series):
    """Normalize a series to a 0-1 range."""
    min_val = series.min()
    max_val = series.max()
    return (series - min_val) / (max_val - min_val) if max_val != min_val else pd.Series(0.5, index=series.index)

def main():
    parser = argparse.ArgumentParser(description='Combined algorithm for data cleaning based on missingness scoring')
    parser.add_argument('--input', type=str, default='output_erased_dataset.csv', help='Input CSV file path')
    parser.add_argument('--output', type=str, default='cleaned_dataset.csv', help='Output CSV file path')
    parser.add_argument('-p', '--percentile', type=int, default=75, help='Missing values percentile threshold (0-100)')
    parser.add_argument('-i', '--image', type=str, default='missing_distribution.png', help='Path for saving distribution plot')
    parser.add_argument('-c', '--important-cols', default='', help='Comma-separated list of important columns')
    parser.add_argument('-w', '--importance-weight', type=float, default=1.0, help='Weight multiplier for important column missing values')
    parser.add_argument('-r', '--min-rows', type=int, default=0, help='Minimum rows to keep')
    parser.add_argument('-m', '--max-missing', type=int, default=0, help='Maximum total missing values in dataset')
    parser.add_argument('-mp','--min-percent', type=float, default=0.0, help='Minimum percent of original rows to retain')
    parser.add_argument('--verbose', action='store_true', help='Print detailed information')

    args = parser.parse_args()
    
    # Parameter validation
    if not 0 <= args.percentile <= 100:
        raise ValueError("Percentile must be between 0 and 100")
    if args.importance_weight < 0:
        raise ValueError("Importance weight must be non-negative")
    if args.min_rows < 0:
        raise ValueError("Minimum rows must be non-negative")
    if args.min_percent < 0 or args.min_percent > 100:
        raise ValueError("Minimum percent must be between 0 and 100")

    # Load data
    try:
        data = pd.read_csv(args.input)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {args.input}")
    except Exception as e:
        raise Exception(f"Error loading data: {str(e)}")
    
    original_rows = len(data)
    if original_rows == 0:
        print("Warning: Input dataset is empty")
        data.to_csv(args.output, index=False)
        return
    
    # Process important columns
    important_cols = [col.strip() for col in args.important_cols.split(',') if col.strip()]
    missing = list(set(important_cols) - set(data.columns))
    if missing:
        raise ValueError(f"Important columns not in dataset: {missing}")

    # Calculate missing values efficiently
    other_cols = [col for col in data.columns if col not in important_cols]
    
    # Vectorized calculation of missing values
    if important_cols and args.importance_weight > 1.0:
        imp_na = data[important_cols].isna().sum(axis=1)
        oth_na = data[other_cols].isna().sum(axis=1)
        na_weighted = imp_na * args.importance_weight + oth_na
    else:
        na_weighted = data.isna().sum(axis=1)
    
    na_total = data.isna().sum(axis=1)
    
    # Calculate score components
    data_size = len(data)
    rank_array = np.arange(data_size)
    
    # Sort indices by weighted NA counts
    sorted_indices = na_weighted.argsort()[::-1]  # descending order
    
    # Use the sorted indices to assign ranks
    ranks = np.empty_like(sorted_indices)
    ranks[sorted_indices] = rank_array
    
    # Normalize both metrics
    norm_missing = normalize(na_weighted)
    norm_rank = normalize(pd.Series(ranks))
    
    # Calculate combined score
    combined_score = norm_missing + norm_rank
    
    # Create a DataFrame for sorting and visualization
    score_df = pd.DataFrame({
        'na_weighted': na_weighted,
        'na_total': na_total,
        'rank_score': ranks,
        'norm_missing': norm_missing,
        'norm_rank': norm_rank,
        'combined_score': combined_score
    })
    
    # Plot distribution
    plt.figure(figsize=(10, 6))
    sns.histplot(combined_score, bins=30, kde=True)
    plt.title('Combined Missingness Score Distribution')
    plt.xlabel('Combined Score')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig(args.image)
    plt.close()

    # Find the threshold based on percentile
    score_threshold = combined_score.quantile(args.percentile / 100)
    
    # Get the indices meeting the initial percentile criterion
    initial_mask = combined_score <= score_threshold
    
    # Optimize constraint application - binary search approach
    if args.max_missing > 0 or args.min_rows > 0 or args.min_percent > 0:
        # Get indices sorted by score (best to worst)
        sorted_by_score = combined_score.sort_values().index
        
        # Binary search to find optimal cutoff
        left, right = 0, sum(initial_mask) - 1
        best_cutoff = left  # Start with keeping all rows that meet percentile
        
        while left <= right:
            mid = (left + right) // 2
            keep_indices = sorted_by_score[:mid+1]
            
            curr_rows = len(keep_indices)
            curr_percent = 100 * curr_rows / original_rows
            curr_missing = na_total.loc[keep_indices].sum()
            
            # Check if we meet all constraints
            if (curr_missing <= args.max_missing or args.max_missing == 0) and \
               (curr_rows <= args.min_rows or args.min_rows == 0) and \
               (curr_percent <= args.min_percent or args.min_percent == 0):
                # This is a valid solution, try to keep more rows
                best_cutoff = mid
                left = mid + 1
            else:
                # We need to be more aggressive in dropping rows
                right = mid - 1
        
        # Use the best cutoff found
        final_indices = sorted_by_score[:best_cutoff+1]
        filtered = data.loc[final_indices].copy()
    else:
        # If no hard constraints, just use percentile filtering
        filtered = data.loc[initial_mask].copy()
    
    # Sort by score for better interpretability
    filtered = filtered.join(score_df[['combined_score']])
    filtered = filtered.sort_values('combined_score')
    filtered = filtered.drop(columns=['combined_score'])
    
    # Save output
    filtered.to_csv(args.output, index=False)
    
    if args.verbose:
        print(f"Original dataset: {original_rows} rows")
        print(f"Filtered dataset: {len(filtered)} rows ({len(filtered)/original_rows:.1%} retained)")
        print(f"Total missing values: {na_total.loc[filtered.index].sum()}")
    
    print(f"Saved cleaned dataset to: {os.path.abspath(args.output)}")
    print(f"Plot saved to: {os.path.abspath(args.image)}")
    print(f"Final row count: {len(filtered)} (from {original_rows})")

if __name__ == "__main__":
    main()