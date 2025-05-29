import argparse
import pandas as pd
import os
import numpy as np

def compute_weighted_missing_vectorized(data, important_cols, weight):
    """Optimized vectorized weighted missing calculation"""
    if data.empty:
        return pd.Series([], dtype=float, index=data.index)
    
    # Use numpy for faster computation
    is_na = data.isna().values
    total_missing = is_na.sum(axis=1)
    
    if not important_cols or weight <= 1.0:
        return pd.Series(total_missing * 1.5, index=data.index)
    
    # Create boolean masks for important columns
    imp_cols = [col for col in important_cols if col in data.columns]
    if not imp_cols:
        return pd.Series(total_missing * 1.5, index=data.index)
    
    # Get column indices for vectorized operations
    imp_indices = [data.columns.get_loc(col) for col in imp_cols]
    other_indices = [i for i in range(len(data.columns)) if i not in imp_indices]
    
    # Vectorized computation
    imp_na = is_na[:, imp_indices].sum(axis=1) if imp_indices else np.zeros(len(data))
    oth_na = is_na[:, other_indices].sum(axis=1) if other_indices else np.zeros(len(data))
    
    return pd.Series((imp_na ** 1.5) * weight + oth_na, index=data.index)

def identify_high_missingness_zones_optimized(data, std_devs=1.5):
    """Optimized zone identification with numpy"""
    if data.empty:
        return pd.Index([])
    
    # Use numpy for faster computation
    missing_per_row = data.isna().sum(axis=1).values
    
    if len(missing_per_row) == 0:
        return pd.Index([])
    
    mean_missing = missing_per_row.mean()
    std_missing = missing_per_row.std()
    
    if std_missing == 0:
        if mean_missing > 0:
            mask = missing_per_row > 0
            return data.index[mask]
        return pd.Index([])
    
    threshold = mean_missing + std_devs * std_missing
    mask = missing_per_row > threshold
    return data.index[mask]

def optimize_column_removal(data, important_cols_set, max_missing, min_cols_required, current_missing):
    """Optimized column removal with vectorized operations"""
    if current_missing <= max_missing or len(data.columns) <= min_cols_required:
        return data, [], current_missing
    
    # Pre-compute all column missing counts using numpy
    col_missing_counts = data.isna().sum()
    removable_cols = [col for col in data.columns if col not in important_cols_set]
    
    if not removable_cols:
        return data, [], current_missing
    
    # Sort removable columns by missing count (descending)
    removable_missing = col_missing_counts[removable_cols].sort_values(ascending=False)
    
    cols_to_remove = []
    missing_reduction = 0
    
    for col in removable_missing.index:
        if len(data.columns) - len(cols_to_remove) <= min_cols_required:
            break
        
        col_missing = removable_missing[col]
        cols_to_remove.append(col)
        missing_reduction += col_missing
        
        if current_missing - missing_reduction <= max_missing:
            break
    
    if cols_to_remove:
        data = data.drop(columns=cols_to_remove)
        current_missing -= missing_reduction
    
    return data, cols_to_remove, current_missing

def main():
    parser = argparse.ArgumentParser(description='Optimized data cleaning with vectorized operations')
    parser.add_argument('--input', type=str, required=True, help='Input CSV file')
    parser.add_argument('--output', type=str, required=True, help='Output CSV file')
    parser.add_argument('-c','--important-cols', default='', help='Comma-separated important columns')
    parser.add_argument('-w','--importance-weight', type=float, default=2.0)
    parser.add_argument('-r','--min-rows', type=int, default=0)
    parser.add_argument('-m','--max-missing', type=int, default=0)
    parser.add_argument('-mp','--min-percent', type=float, default=0.0)
    parser.add_argument('-ct','--col-threshold', type=int, default=0)
    parser.add_argument('-crt','--col-relative-threshold', type=float, default=0.0)
    parser.add_argument('-sd','--std-devs', type=float, default=1.5,
                        help='Standard deviations above mean for zone threshold')
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    # Load data
    print(f'Loading data from {args.input}...')
    data = pd.read_csv(args.input, low_memory=False)
    important_cols = [c.strip() for c in args.important_cols.split(',') if c.strip()]
    
    # Calculate constraints
    min_rows_required = max(args.min_rows, int(len(data) * max(0, min(100, args.min_percent)) / 100))
    min_cols_required = max(args.col_threshold, int(len(data.columns) * max(0, min(100, args.col_relative_threshold)) / 100))
    
    current = data.copy()
    original_rows, original_cols = current.shape
    current_missing = current.isna().sum().sum()
    important_cols_set = set(important_cols)
    
    print(f'[START] {original_rows} rows, {original_cols} cols, {current_missing} missing')
    print(f'[CONSTRAINTS] min_rows={min_rows_required}, max_missing={args.max_missing}, min_cols={min_cols_required}')
    
    # PHASE 1: Optimized Column removal
    current, removed_cols, current_missing = optimize_column_removal(
        current, important_cols_set, args.max_missing, min_cols_required, current_missing
    )
    
    if args.verbose and removed_cols:
        print(f'[COL REMOVAL] Removed {len(removed_cols)} columns')
    
    # Early exit if constraints are met
    if current_missing <= args.max_missing:
        print('[EARLY EXIT] Missing value constraint met after column removal')
    else:
        # PHASE 2: Optimized zone-based row removal
        high_missing_zone = identify_high_missingness_zones_optimized(current, args.std_devs)
        
        if args.verbose:
            print(f'[ZONES] High-missing zone: {len(high_missing_zone)} rows')
        
        # Pre-compute row weights for the entire zone to avoid recalculation
        if len(high_missing_zone) > 0 and len(current) > min_rows_required:
            zone_data = current.loc[high_missing_zone]
            zone_weights = compute_weighted_missing_vectorized(
                zone_data, important_cols, args.importance_weight
            )
            zone_missing_per_row = zone_data.isna().sum(axis=1)
            
            # Sort zone rows by weight (worst first) and remove iteratively
            sorted_zone_indices = zone_weights.sort_values(ascending=False).index
            
            for worst_row in sorted_zone_indices:
                if current_missing <= args.max_missing:
                    break
                if len(current) <= min_rows_required:
                    break
                
                row_missing_count = zone_missing_per_row[worst_row]
                current = current.drop(index=[worst_row])
                current_missing -= row_missing_count
                
                if args.verbose and len(sorted_zone_indices) <= 100:  # Only log for smaller zones
                    print(f'[ZONE REMOVAL] row {worst_row} ({row_missing_count} missing)')
        
        # PHASE 3: Global fallback removal
        if current_missing > args.max_missing and len(current) > min_rows_required:
            if args.verbose:
                print('[FALLBACK] Global row removal')
            
            # Pre-compute all weights to avoid recalculation
            global_weights = compute_weighted_missing_vectorized(
                current, important_cols, args.importance_weight
            )
            global_missing_per_row = current.isna().sum(axis=1)
            
            # Sort all rows by weight and remove iteratively
            sorted_global_indices = global_weights.sort_values(ascending=False).index
            
            for worst_row in sorted_global_indices:
                if current_missing <= args.max_missing:
                    break
                if len(current) <= min_rows_required:
                    break
                
                row_missing_count = global_missing_per_row[worst_row]
                current = current.drop(index=[worst_row])
                current_missing -= row_missing_count
                
                if args.verbose and len(current) % 1000 == 0:  # Log every 1000 removals
                    print(f'[FALLBACK] {len(current)} rows remaining')

    # FINAL OUTPUT
    current_rows = len(current)
    current_percent = (current_rows / original_rows) * 100
    final_missing = current.isna().sum().sum()
    
    constraints_met = (
        final_missing <= args.max_missing and
        current_rows <= min_rows_required and
        current_percent <= args.min_percent
    )
    
    print('\n[RESULTS]')
    print(f'Rows: {current_rows}/{original_rows} ({current_percent:.1f}%)')
    print(f'Columns: {len(current.columns)}/{original_cols}')
    print(f'Missing values: {final_missing}')
    print(f'Constraints: {"MET" if constraints_met else "NOT MET"}')
    
    if removed_cols:
        print(f'Removed columns: {", ".join(removed_cols[:5])}' + 
              (f'... (+{len(removed_cols)-5} more)' if len(removed_cols) > 5 else ''))
    
    current.to_csv(args.output, index=False)
    print(f'Output saved to: {os.path.abspath(args.output)}')

if __name__ == '__main__':
    main()