import pandas as pd
import numpy as np
import argparse

parser = argparse.ArgumentParser(
    description="Generate a random numerical dataset with specified rows and columns."
)
parser.add_argument(
    "--columns", "-c",
    type=int,
    required=True,
    help="Number of columns to generate"
)
parser.add_argument(
    "--rows", "-r",
    type=int,
    required=True,
    help="Number of rows to generate"
)
parser.add_argument(
    "--output",
    type=str,
    default="output_complete_dataset.csv",
    help="Output CSV file name (default: output_complete_dataset.csv)"
)

args = parser.parse_args()
columns = args.columns
rows = args.rows

# Generate random numerical data
data = np.random.randint(-1000000, 1000001, size=(rows, columns))

# Create the DataFrame with column names col_1, col_2, ...
df = pd.DataFrame(data, columns=[f'col_{i+1}' for i in range(columns)])

# Display the first few rows
print(df.head())

# Save the DataFrame to CSV
df.to_csv(args.output, index=False)
print(f"Complete DataFrame written to '{args.output}'")
