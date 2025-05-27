import pandas as pd
from queue import PriorityQueue
import argparse

def branch_and_bound(df, important_cols, imp_weight, min_rows, min_cols, max_col_missing):
    print("Starting branch-and-bound optimization...")
    orig_total_missing = df.isna().sum(axis=1)
    orig_imp_missing = df[important_cols].isna().sum(axis=1) if important_cols else pd.Series(0, index=df.index)
    num_important = len(important_cols) if important_cols else 1

    row_scores = orig_total_missing * (1 + imp_weight * (orig_imp_missing / num_important))

    best = {'df': None, 'cost': float('inf')}
    pq = PriorityQueue()
    pq.put((0, df, 0, 0))  # (priority, current_df, rows_removed, cols_removed)

    iteration = 0
    while not pq.empty():
        iteration += 1
        print(f"\nIteration {iteration}: Queue size = {pq.qsize()}")

        _, current_df, n_rows, n_cols = pq.get()
        print(f"Evaluating state with cost = {n_rows + n_cols}, rows = {current_df.shape[0]}, cols = {current_df.shape[1]}")

        if (n_rows + n_cols) >= best['cost']:
            print("Pruned: cost >= current best.")
            continue

        current_cols = current_df.shape[1]
        current_rows = current_df.shape[0]
        col_missing = current_df.isna().mean().max()

        if (current_rows >= min_rows and 
            current_cols >= min_cols and 
            col_missing <= max_col_missing):
            print("Feasible solution found.")
            if (n_rows + n_cols) < best['cost']:
                print(f"New best solution with cost {n_rows + n_cols}")
                best = {'df': current_df.copy(), 'cost': n_rows + n_cols}
            continue

        # Branch on rows
        if current_rows > min_rows:
            remaining_scores = row_scores.reindex(current_df.index)
            if not remaining_scores.empty:
                worst_row = remaining_scores.idxmax()
                print(f"Branching: dropping row {worst_row}")
                new_df = current_df.drop(index=worst_row)
                pq.put((n_rows + 1, new_df, n_rows + 1, n_cols))

        # Branch on columns
        if current_cols > min_cols:
            col_scores = current_df.isna().mean()
            if not col_scores.empty:
                worst_col = col_scores.idxmax()
                print(f"Branching: dropping column '{worst_col}'")
                new_df = current_df.drop(columns=[worst_col])
                pq.put((n_cols + 1, new_df, n_rows, n_cols + 1))

    print("\nBranch-and-bound complete.")
    return best['df'], best['cost']

def parse_args():
    parser = argparse.ArgumentParser(description="Run branch-and-bound cleaning on a dataset.")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to input CSV file")
    parser.add_argument("--output", "-o", type=str, default="cleaned_dataset.csv", help="Path to save the cleaned dataset")
    parser.add_argument("--important-cols", "-c", type=str, default="", help="Comma-separated list of important columns")
    parser.add_argument("--importance-weight", "-w", type=float, default=1.0, help="Weight for important columns (default: 1.0)")
    parser.add_argument("--min-rows", "-r", type=int, required=True, help="Minimum number of rows to keep")
    parser.add_argument("--min-cols", "-l", type=int, required=True, help="Minimum number of columns to keep")
    parser.add_argument("--max-col-missing", "-m", type=float, required=True, help="Maximum allowed missing % per column (e.g., 0.5 for 50%%)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    df = pd.read_csv(args.input)
    important_cols = [col.strip() for col in args.important_cols.split(',') if col.strip()]
    
    result, cost = branch_and_bound(
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
        print(f"Cleaned dataset saved to: {args.output}")
    else:
        print("No feasible solution found with given parameters.")
