import pandas as pd
import numpy as np
import random
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
    description="Randomly erase a percentage of values (MCAR) in a random subset of columns."
)
parser.add_argument(
    "--input", "-i",
    default="output_complete_dataset.csv",
    help="Path to input CSV file"
)
parser.add_argument(
    "--num_columns", "-n",
    type=int,
    required=True,
    help="Number of columns (randomly chosen) to apply MCAR missingness"
)
parser.add_argument(
    "--percentage", "-p",
    type=float,
    required=True,
    help="Percentage of entries to erase in each selected column (0–100)"
)
parser.add_argument(
    "--output", "-o",
    default="output_erased_dataset.csv",
    help="Path for the output CSV file"
)
parser.add_argument(
    "--gpu",
    action="store_true",
    help="Use GPU acceleration if available"
)
args = parser.parse_args()

# Step 1: Load the CSV file
print(f"Loading data from {args.input}...")
data = pd.read_csv(args.input)
rows, cols = data.shape
print(f"Dataset shape: {rows} rows × {cols} columns")

if args.num_columns > cols:
    raise ValueError(f"num_columns={args.num_columns} exceeds total columns={cols}")

# Step 2: Randomly choose columns
all_cols = list(data.columns)
selected_cols = random.sample(all_cols, args.num_columns)
print(f"Selected columns for MCAR ({args.num_columns}): {selected_cols}")

# Number of values to erase per column
num_erase_per_col = int(rows * (args.percentage / 100.0))
print(f"Erasing {num_erase_per_col} entries per selected column "
      f"({args.percentage:.2f}% of each column)")

# Step 3: Choose between GPU or CPU processing
use_gpu = CUDA_AVAILABLE and args.gpu
print(f"Using {'GPU' if use_gpu else 'CPU'} processing...\n")

if use_gpu:
    # Transfer full data to GPU array
    data_gpu = cp.array(data.values, dtype=float)  # cast to float for NaN support

    for col in selected_cols:
        cidx = all_cols.index(col)
        # Draw unique row indices to erase in this column
        erase_rows = cp.random.choice(
            rows, size=num_erase_per_col, replace=False
        )
        # Set those positions to NaN
        data_gpu[erase_rows, cidx] = cp.nan
        print(f"Column '{col}': erased {num_erase_per_col} values")

    # Build DataFrame back on CPU
    result = cp.asnumpy(data_gpu)
    data = pd.DataFrame(result, columns=all_cols)

else:
    for col in selected_cols:
        # Randomly pick row indices
        erase_rows = random.sample(range(rows), num_erase_per_col)
        # Set them to None/NaN
        data.loc[erase_rows, col] = np.nan
        print(f"Column '{col}': erased {num_erase_per_col} values")

# Step 4: Show a preview and save
print("\nFirst 5 rows of modified data:")
print(data.head())

data.to_csv(args.output, index=False)
print(f"\nModified dataset saved to '{args.output}'")
