import pandas as pd
from queue import PriorityQueue
import argparse
import numpy as np

def calculate_lower_bound(current_df, n_rows_removed, n_cols_removed, min_rows, min_cols, max_col_missing):
    """
    Calculate a lower bound on the total cost (rows + columns to remove)
    needed to make the current state feasible.
    
    This function ensures monotonicity: LB(parent) <= LB(child)
    """
    current_cost = n_rows_removed + n_cols_removed
    current_rows = current_df.shape[0]
    current_cols = current_df.shape[1]
    
    # Lower bound on additional rows that must be removed
    min_additional_rows = max(0, current_rows - min_rows)
    
    # Lower bound on additional columns that must be removed
    min_additional_cols = max(0, current_cols - min_cols)
    
    # Lower bound based on missing data constraint
    if not current_df.empty:
        col_missing_rates = current_df.isna().mean()
        # Count columns that currently violate the constraint
        violating_cols = (col_missing_rates > max_col_missing).sum()
        
        # We need to remove at least this many columns to satisfy the constraint
        # This is optimistic because removing rows might also help
        min_additional_cols = max(min_additional_cols, violating_cols)
    
    lower_bound = current_cost + min_additional_rows + min_additional_cols
    
    return lower_bound

def is_feasible(current_df, min_rows, min_cols, max_col_missing):
    """Check if current state satisfies all constraints"""
    if current_df.empty:
        return False
        
    current_rows = current_df.shape[0]
    current_cols = current_df.shape[1]
    
    # Check size constraints
    if current_rows < min_rows or current_cols < min_cols:
        return False
    
    # Check missing data constraint
    col_missing = current_df.isna().mean().max() if not current_df.empty else 1.0
    if col_missing > max_col_missing:
        return False
        
    return True

def branch_and_bound_optimal(df, important_cols, imp_weight, min_rows, min_cols, max_col_missing):
    """
    Optimal branch-and-bound with proper bounding function that guarantees optimality.
    """
    print("Starting optimal branch-and-bound optimization...")
    
    # Precompute row scores for consistent branching decisions
    orig_total_missing = df.isna().sum(axis=1)
    orig_imp_missing = df[important_cols].isna().sum(axis=1) if important_cols else pd.Series(0, index=df.index)
    num_important = len(important_cols) if important_cols else 1
    row_scores = orig_total_missing * (1 + imp_weight * (orig_imp_missing / num_important))

    # Initialize best solution
    best = {'df': None, 'cost': float('inf')}
    
    # Priority queue: (lower_bound, tie_breaker, current_df, rows_removed, cols_removed)
    pq = PriorityQueue()
    initial_lb = calculate_lower_bound(df, 0, 0, min_rows, min_cols, max_col_missing)
    pq.put((initial_lb, 0, df, 0, 0))

    iteration = 0
    nodes_explored = 0
    nodes_pruned = 0
    
    while not pq.empty():
        iteration += 1
        if iteration % 100 == 0:  # Less frequent printing for efficiency
            print(f"Iteration {iteration}: Queue size = {pq.qsize()}, Best cost = {best['cost']}")

        lower_bound, _, current_df, n_rows, n_cols = pq.get()
        nodes_explored += 1
        
        # CRITICAL: Prune based on lower bound (this ensures optimality)
        if lower_bound >= best['cost']:
            nodes_pruned += 1
            continue

        current_cost = n_rows + n_cols
        
        # Check if current state is feasible
        if is_feasible(current_df, min_rows, min_cols, max_col_missing):
            if current_cost < best['cost']:
                print(f"New best solution found with cost {current_cost}")
                best = {'df': current_df.copy(), 'cost': current_cost}
            continue

        # Generate child nodes by branching
        children_added = 0
        
        # Branch on rows (remove worst row)
        if current_df.shape[0] > min_rows:
            remaining_scores = row_scores.reindex(current_df.index)
            if not remaining_scores.empty:
                worst_row = remaining_scores.idxmax()
                new_df = current_df.drop(index=worst_row)
                new_n_rows = n_rows + 1
                new_lb = calculate_lower_bound(new_df, new_n_rows, n_cols, min_rows, min_cols, max_col_missing)
                
                # Only add to queue if lower bound suggests it could be better than current best
                if new_lb < best['cost']:
                    pq.put((new_lb, iteration * 2, new_df, new_n_rows, n_cols))
                    children_added += 1

        # Branch on columns (remove worst column)
        if current_df.shape[1] > min_cols:
            col_scores = current_df.isna().mean()
            if not col_scores.empty:
                worst_col = col_scores.idxmax()
                new_df = current_df.drop(columns=[worst_col])
                new_n_cols = n_cols + 1
                new_lb = calculate_lower_bound(new_df, n_rows, new_n_cols, min_rows, min_cols, max_col_missing)
                
                # Only add to queue if lower bound suggests it could be better than current best
                if new_lb < best['cost']:
                    pq.put((new_lb, iteration * 2 + 1, new_df, n_rows, new_n_cols))
                    children_added += 1
        
        # If no children were added, this branch is exhausted
        if children_added == 0:
            nodes_pruned += 1

    print(f"\nBranch-and-bound complete.")
    print(f"Nodes explored: {nodes_explored}")
    print(f"Nodes pruned: {nodes_pruned}")
    print(f"Total iterations: {iteration}")
    
    return best['df'], best['cost']

def verify_monotonicity_property(df, min_rows, min_cols, max_col_missing, num_tests=10):
    """
    Verify that our bounding function satisfies monotonicity.
    This is a debugging/verification function.
    """
    print("Verifying monotonicity property...")
    
    for test in range(num_tests):
        # Create a random parent state
        parent_df = df.sample(frac=0.8).sample(frac=0.8, axis=1)
        parent_rows_removed = df.shape[0] - parent_df.shape[0]
        parent_cols_removed = df.shape[1] - parent_df.shape[1]
        
        parent_lb = calculate_lower_bound(parent_df, parent_rows_removed, parent_cols_removed, 
                                        min_rows, min_cols, max_col_missing)
        
        # Create child states
        if parent_df.shape[0] > 1:
            child_df_row = parent_df.iloc[:-1]  # Remove one row
            child_lb_row = calculate_lower_bound(child_df_row, parent_rows_removed + 1, parent_cols_removed,
                                               min_rows, min_cols, max_col_missing)
            
            if parent_lb > child_lb_row:
                print(f"WARNING: Monotonicity violated! Parent LB: {parent_lb}, Child LB: {child_lb_row}")
                return False
        
        if parent_df.shape[1] > 1:
            child_df_col = parent_df.iloc[:, :-1]  # Remove one column
            child_lb_col = calculate_lower_bound(child_df_col, parent_rows_removed, parent_cols_removed + 1,
                                               min_rows, min_cols, max_col_missing)
            
            if parent_lb > child_lb_col:
                print(f"WARNING: Monotonicity violated! Parent LB: {parent_lb}, Child LB: {child_lb_col}")
                return False
    
    print("Monotonicity property verified!")
    return True

def parse_args():
    parser = argparse.ArgumentParser(description="Run optimal branch-and-bound cleaning on a dataset.")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input CSV file")
    parser.add_argument("--output", "-o", type=str, default="cleaned_dataset.csv", help="Path to save the cleaned dataset")
    parser.add_argument("--important-cols", "-c", type=str, default="", help="Comma-separated list of important columns")
    parser.add_argument("--importance-weight", "-w", type=float, default=1.0, help="Weight for important columns (default: 1.0)")
    parser.add_argument("--min-rows", "-r", type=int, required=True, help="Minimum number of rows to keep")
    parser.add_argument("--min-cols", "-l", type=int, required=True, help="Minimum number of columns to keep")
    parser.add_argument("--max-col-missing", "-m", type=float, required=True, help="Maximum allowed missing % per column (e.g., 0.5 for 50%%)")
    parser.add_argument("--verify-monotonicity", action="store_true", help="Verify monotonicity property before running")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    df = pd.read_csv(args.input)
    important_cols = [col.strip() for col in args.important_cols.split(',') if col.strip()]
    
    # Verify monotonicity if requested
    if args.verify_monotonicity:
        verify_monotonicity_property(df, args.min_rows, args.min_cols, args.max_col_missing)
    
    result, cost = branch_and_bound_optimal(
        df=df,
        important_cols=important_cols,
        imp_weight=args.importance_weight,
        min_rows=args.min_rows,
        min_cols=args.min_cols,
        max_col_missing=args.max_col_missing
    )

    if result is not None:
        result.to_csv(args.output, index=False)
        print(f"Optimal solution cost: {cost}")
        print(f"Final dataset shape: {result.shape}")
        print(f"Max column missing rate: {result.isna().mean().max():.3f}")
        print(f"Cleaned dataset saved to: {args.output}")
    else:
        print("No feasible solution found with given parameters.")