import pandas as pd
import numpy as np
import argparse

# Simple check for CUDA availability
try:
    import cupy as cp
    CUDA_AVAILABLE = True
    print("CUDA is available! GPU acceleration can be used.")
except ImportError:
    CUDA_AVAILABLE = False
    print("CUDA not available. Will use CPU processing only.")

parser = argparse.ArgumentParser(
    description="Apply MNAR (Missing Not At Random) missingness to multiple columns based on their own values."
)
parser.add_argument("--input", "-i", default="output_complete_dataset.csv", help="Path to input CSV file")

parser.add_argument("--column", "-c", nargs='+', required=True, help="List of columns to apply MNAR to")
parser.add_argument("--cutoff", type=float, nargs='+', required=True, help="List of cutoff values for MNAR")
parser.add_argument("--pi_high", type=float, nargs='+', required=True, help="List of pi_high values")
parser.add_argument("--pi_low", type=float, nargs='+', required=True, help="List of pi_low values")

parser.add_argument("--seed", "-s", type=int, default=123, help="Random seed for reproducibility")
parser.add_argument("--output", "-o", default="output_erased_dataset.csv", help="Path to output CSV file")
parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration if available")

args = parser.parse_args()

# Validation
n_rules = len(args.column)
if not (len(args.cutoff) == len(args.pi_high) == len(args.pi_low) == n_rules):
    raise ValueError("All MNAR parameter lists must be the same length.")

# Load dataset
print(f"Loading data from {args.input}...")
data = pd.read_csv(args.input)
print(f"Dataset shape: {data.shape}")

use_gpu = CUDA_AVAILABLE and args.gpu
print(f"Using {'GPU' if use_gpu else 'CPU'} processing...\n")

# Set random seed
if use_gpu:
    cp.random.seed(args.seed)
else:
    np.random.seed(args.seed)

# Apply MNAR missingness
for idx, (col, cutoff, pi_h, pi_l) in enumerate(zip(args.column, args.cutoff, args.pi_high, args.pi_low)):
    print(f"\n--- MNAR Rule {idx + 1} ---")
    print(f"Column: {col}, Cutoff: {cutoff}, pi_high: {pi_h}, pi_low: {pi_l}")

    if col not in data.columns:
        raise ValueError(f"Column '{col}' not found in dataset.")

    values = data[col].values
    n_rows = len(data)

    if use_gpu:
        values_gpu = cp.array(values)
        high_condition = values_gpu >= cutoff
        n_high = cp.sum(high_condition).item()
        n_low = n_rows - n_high

        print(f"High: {n_high} ({n_high/n_rows:.2%}), Low: {n_low} ({n_low/n_rows:.2%})")

        uniform_random = cp.random.uniform(0, 1, n_rows)
        missing_indicator = cp.where(high_condition, uniform_random < pi_h, uniform_random < pi_l)

        num_missing = cp.sum(missing_indicator).item()
        print(f"Missing values to introduce: {num_missing} ({num_missing/n_rows:.2%})")

        if values_gpu.dtype.kind in ['i', 'u']:
            values_gpu = values_gpu.astype(cp.float32)
        values_missing = cp.where(missing_indicator, cp.nan, values_gpu)

        data[col] = cp.asnumpy(values_missing)

    else:
        high_condition = values >= cutoff
        n_high = np.sum(high_condition)
        n_low = n_rows - n_high

        print(f"High: {n_high} ({n_high/n_rows:.2%}), Low: {n_low} ({n_low/n_rows:.2%})")

        uniform_random = np.random.uniform(0, 1, n_rows)
        missing_indicator = np.where(high_condition, uniform_random < pi_h, uniform_random < pi_l)

        num_missing = np.sum(missing_indicator)
        print(f"Missing values to introduce: {num_missing} ({num_missing/n_rows:.2%})")

        values_missing = values.copy()
        if values_missing.dtype.kind in ['i', 'u']:
            values_missing = values_missing.astype(float)
        values_missing[missing_indicator] = np.nan

        data[col] = values_missing

# Final summary
print("\n--- Final Missingness Summary ---")
for col in args.column:
    total_missing = data[col].isna().sum()
    print(f"{col}: {total_missing} missing ({total_missing/len(data):.2%})")

# Save modified dataset
data.to_csv(args.output, index=False)
print(f"\nModified dataset saved to '{args.output}'")
