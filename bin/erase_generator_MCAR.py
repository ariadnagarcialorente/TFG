import pandas as pd
import random
import argparse

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
args = parser.parse_args()

# Load dataset from CSV file
data = pd.read_csv(args.input)

# Calculate total number of data points
total_values = data.size
num_erase = int(total_values * (args.percentage / 100.0))
print(f"Total values in dataset: {total_values}")
print(f"Number of values to erase: {num_erase}")

# Create list of all possible (row, column) coordinates in the dataframe
indices = [(i, j) for i in range(data.shape[0]) for j in range(data.shape[1])]

# Randomly select coordinates to erase
to_delete = random.sample(indices, num_erase)

# Replace selected values with None
for idx, (row, col) in enumerate(to_delete):
    data.iloc[row, col] = None
    
    # Print progress every 50000 iterations
    if (idx + 1) % 50000 == 0:
        print(f"Progress: {idx + 1}/{num_erase} values erased ({(idx + 1)/num_erase*100:.2f}%)")

# Print final progress if not already printed
if num_erase % 1000 != 0:
    print(f"Progress: {num_erase}/{num_erase} values erased (100.00%)")

# Display first 5 rows of modified data
print("\nFirst 5 rows of modified data:")
print(data.head())

# Save modified dataset to new CSV file
data.to_csv(args.output, index=False)

# Confirm completion
print(f"\nComplete DataFrame written to '{args.output}'")