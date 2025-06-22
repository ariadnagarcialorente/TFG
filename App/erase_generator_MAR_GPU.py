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
    description="Apply MAR (Missing At Random) missingness to multiple target columns based on reference columns."
)
parser.add_argument("--input", "-i", default="output_complete_dataset.csv", help="Path to input CSV file")

parser.add_argument("--reference_column", "-r", nargs='+', required=True, help="List of reference columns")
parser.add_argument("--target_column", "-t", nargs='+', required=True, help="List of target columns")
parser.add_argument("--cutoff", "-c", type=float, nargs='+', default=[], help="List of cutoff values")
parser.add_argument("--pi_high", type=float, nargs='+', default=[], help="List of pi_high values")
parser.add_argument("--pi_low", type=float, nargs='+', default=[], help="List of pi_low values")

parser.add_argument("--seed", "-s", type=int, default=123, help="Random seed for reproducibility")
parser.add_argument("--output", "-o", default="output_erased_dataset.csv", help="Path to output CSV file")
parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration if available")

args = parser.parse_args()

# Validation
n_rules = len(args.reference_column)
if not (len(args.target_column) == len(args.cutoff) == len(args.pi_high) == len(args.pi_low) == n_rules):
    raise ValueError("All MAR parameter lists must be the same length.")

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

# Process each MAR rule
for idx, (ref_col, tgt_col, cutoff, pi_h, pi_l) in enumerate(zip(
    args.reference_column,
    args.target_column,
    args.cutoff,
    args.pi_high,
    args.pi_low
)):
    print(f"\n--- MAR Rule {idx + 1} ---")
    print(f"Reference: {ref_col}, Target: {tgt_col}, Cutoff: {cutoff}, pi_high: {pi_h}, pi_low: {pi_l}")

    if ref_col not in data.columns or tgt_col not in data.columns:
        raise ValueError(f"Column mismatch: {ref_col} or {tgt_col} not found in dataset.")

    ref_values = data[ref_col].values
    tgt_values = data[tgt_col].values
    n_rows = len(data)

    if use_gpu:
        # GPU version
        ref_gpu = cp.array(ref_values)
        tgt_gpu = cp.array(tgt_values)

        high_condition = ref_gpu >= cutoff
        n_high = cp.sum(high_condition).item()
        n_low = n_rows - n_high

        print(f"High: {n_high} ({n_high/n_rows:.2%}), Low: {n_low} ({n_low/n_rows:.2%})")

        uniform_random = cp.random.uniform(0, 1, n_rows)
        missing_indicator = cp.where(high_condition, uniform_random < pi_h, uniform_random < pi_l)

        num_missing = cp.sum(missing_indicator).item()
        print(f"Missing values to introduce: {num_missing} ({num_missing/n_rows:.2%})")

        if tgt_gpu.dtype.kind in ['i', 'u']:
            tgt_gpu = tgt_gpu.astype(cp.float32)
        tgt_missing = cp.where(missing_indicator, cp.nan, tgt_gpu)

        # Transfer back to CPU
        data[tgt_col] = cp.asnumpy(tgt_missing)

    else:
        # CPU version
        high_condition = ref_values >= cutoff
        n_high = np.sum(high_condition)
        n_low = n_rows - n_high

        print(f"High: {n_high} ({n_high/n_rows:.2%}), Low: {n_low} ({n_low/n_rows:.2%})")

        uniform_random = np.random.uniform(0, 1, n_rows)
        missing_indicator = np.where(high_condition, uniform_random < pi_h, uniform_random < pi_l)

        num_missing = np.sum(missing_indicator)
        print(f"Missing values to introduce: {num_missing} ({num_missing/n_rows:.2%})")

        tgt_missing = tgt_values.copy()
        if tgt_missing.dtype.kind in ['i', 'u']:
            tgt_missing = tgt_missing.astype(float)
        tgt_missing[missing_indicator] = np.nan

        data[tgt_col] = tgt_missing

# Final summary
print("\n--- Final Missingness Summary ---")
for tgt_col in args.target_column:
    total_missing = data[tgt_col].isna().sum()
    print(f"{tgt_col}: {total_missing} missing ({total_missing/len(data):.2%})")

# Save modified dataset
data.to_csv(args.output, index=False)
print(f"\nModified dataset saved to '{args.output}'")
