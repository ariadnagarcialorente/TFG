import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

parser = argparse.ArgumentParser(description="Generate heatmap of missing/present values")
parser.add_argument("--input", "-i", required=True, help="Path to input CSV file")
parser.add_argument("--output", "-o", default="heatmap.png", help="Output path for heatmap image")
args = parser.parse_args()

print(f"Loading data from {args.input}...")
data = pd.read_csv(args.input)

# Convert data to binary (1 for present values, 0 for missing values)
binary_data = data.notna().astype(int)

# Calculate figure size - simplified and fixed
width = min(50, len(data.columns) * 0.01)  # 0.01 inches per column
height = min(50, len(data) * 0.001)        # 0.001 inches per row

# Create figure
plt.figure(figsize=(width, height))

# Generate heatmap - disable labels for large datasets
if len(data) > 1000 or len(data.columns) > 100:
    heatmap = sns.heatmap(binary_data, cbar=True, yticklabels=False, xticklabels=False)
else:
    heatmap = sns.heatmap(binary_data, cbar=True)

# Remove axis labels for cleaner visualization
plt.xlabel("")
plt.ylabel("")
plt.xticks([])
plt.yticks([])

# Customize colorbar
colorbar = heatmap.collections[0].colorbar
colorbar.set_ticks([0, 1])
colorbar.set_ticklabels(["Missing (0)", "Present (1)"])

# Save high-resolution image
plt.savefig(args.output, bbox_inches='tight', pad_inches=0.5, format='png', dpi=150)
print(f"Heatmap saved to {args.output}")