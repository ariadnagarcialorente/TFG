# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn
import argparse

parser = argparse.ArgumentParser(
    description="Randomly erase a percentage of values in a CSV dataset."
)
parser.add_argument(
    "--input",
    "-i",
    required=True,
    help="Path to input CSV file"
)

args = parser.parse_args()

# Step 1: Load the CSV file
print(f"Loading data from {args.input}...")
data = pd.read_csv(args.input)


# Convert data to binary (1 for present values, 0 for missing values)
binary_data = data.notna().astype(int)

# Create a new figure
plt.figure()

# Generate heatmap of missing/present values
fig = sn.heatmap(binary_data, cbar=True)

# Remove x-axis label and ticks for cleaner visualization
plt.xlabel("")
plt.xticks([])

# Remove y-axis label and ticks for cleaner visualization
plt.ylabel("")
plt.yticks([])

# Customize the colorbar with descriptive labels
colorbar = fig.collections[0].colorbar
colorbar.set_ticks([0, 1])
colorbar.set_ticklabels(["Missing (0)", "Present (1)"])

# Save high-resolution image
plt.savefig("heatmap.png", pad_inches=2, format='png', dpi=1200)