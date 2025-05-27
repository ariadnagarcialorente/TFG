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
    description="Randomly erase a percentage of values in a CSV dataset."
)
parser.add_argument(
    "--input",
    "-i",
    default="output_complete_dataset.csv",
    help="Path to input CSV file"
)
parser.add_argument(
    "--percentage",
    "-p",
    type=float,
    required=True,
    help="Percentage of data points to erase (0-100)"
)
parser.add_argument(
    "--output",
    "-o",
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

# Step 2: Calculate how many values to erase
total_values = data.size
num_erase = int(total_values * (args.percentage / 100.0))
print(f"Total values in dataset: {total_values}")
print(f"Number of values to erase: {num_erase}")

# Step 3: Choose between GPU or CPU processing
use_gpu = CUDA_AVAILABLE and args.gpu

if use_gpu:
    print("Using GPU acceleration...")
    
    # Convert DataFrame to NumPy array for GPU processing
    data_values = data.values
    
    # Transfer data to GPU
    data_gpu = cp.array(data_values)
    
    # Step 4: Generate random indices for erasure
    # First, create all possible indices
    rows, cols = data.shape
    all_indices = cp.arange(rows * cols)
    
    # Randomly select indices to erase
    erase_indices = cp.random.choice(all_indices, size=num_erase, replace=False)
    
    # Convert linear indices to row and column indices
    erase_rows = erase_indices // cols
    erase_cols = erase_indices % cols
    
    # Step 5: Create a mask array for the values to keep
    mask = cp.ones((rows, cols), dtype=bool)
    
    # Show progress in smaller batches
    batch_size = 10000
    num_batches = (num_erase + batch_size - 1) // batch_size  # Ceiling division
    
    for b in range(num_batches):
        start_idx = b * batch_size
        end_idx = min((b + 1) * batch_size, num_erase)
        
        # Set mask to False for indices to erase in this batch
        batch_rows = erase_rows[start_idx:end_idx]
        batch_cols = erase_cols[start_idx:end_idx]
        
        for i in range(len(batch_rows)):
            mask[batch_rows[i], batch_cols[i]] = False
        
        # Show progress
        if (b + 1) % 10 == 0 or b == num_batches - 1:
            print(f"Progress: {end_idx}/{num_erase} positions marked for erasure ({end_idx/num_erase*100:.2f}%)")
    
    # Step 6: Apply the mask to erase values
    # Create a float array with NaN values
    nan_array = cp.empty_like(data_gpu, dtype=float)
    nan_array.fill(cp.nan)
    
    # Use the mask to select between original values and NaN
    result_gpu = cp.where(mask, data_gpu, nan_array)
    
    # Step 7: Transfer back to CPU and convert to DataFrame
    result_cpu = cp.asnumpy(result_gpu)
    data = pd.DataFrame(result_cpu, columns=data.columns)
    
else:
    print("Using CPU processing...")
    
    # Step 4: Create list of all possible (row, column) coordinates
    indices = [(i, j) for i in range(data.shape[0]) for j in range(data.shape[1])]
    
    # Step 5: Randomly select coordinates to erase
    to_delete = random.sample(indices, num_erase)
    
    # Step 6: Replace selected values with None
    for idx, (row, col) in enumerate(to_delete):
        data.iloc[row, col] = None
        
        # Print progress every 50000 iterations
        if (idx + 1) % 50000 == 0:
            print(f"Progress: {idx + 1}/{num_erase} values erased ({(idx + 1)/num_erase*100:.2f}%)")
    
    # Print final progress
    if num_erase % 50000 != 0:
        print(f"Progress: {num_erase}/{num_erase} values erased (100.00%)")

# Display first 5 rows of modified data
print("\nFirst 5 rows of modified data:")
print(data.head())

# Save modified dataset to new CSV file
data.to_csv(args.output, index=False)

print(f"Modified data saved to '{args.output}'")