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

# Calculate figure size based on dataset size
if len(data) > 5000 or len(data.columns) > 500:
    # For very large datasets, use fixed large size
    width = 24
    height = 18
else:
    # For smaller datasets, scale appropriately
    width = min(20, max(8, len(data.columns) * 0.1))   # 0.1 inches per column, min 8, max 20
    height = min(16, max(6, len(data) * 0.01))          # 0.01 inches per row, min 6, max 16

# Create figure
plt.figure(figsize=(width, height))

# Generate heatmap - remove grid lines for large datasets to improve visibility
if len(data) > 5000 or len(data.columns) > 500:
    heatmap = sns.heatmap(binary_data, cmap=['red', 'green'], cbar=True, 
                         yticklabels=False, xticklabels=False, vmin=0, vmax=1)
else:
    heatmap = sns.heatmap(binary_data, cmap=['red', 'green'], cbar=True, 
                         yticklabels=False, vmin=0, vmax=1,
                         linewidths=0.01, linecolor='white')

# Remove axis labels and ticks
plt.xlabel("")
plt.ylabel("")
plt.yticks([])
plt.xticks([])  # Remove x-axis labels for large datasets

# Customize colorbar with only two colors/labels
colorbar = heatmap.collections[0].colorbar
colorbar.set_ticks([0.25, 0.75])  # Position labels at center of each color
colorbar.set_ticklabels(["Missing", "Present"])

# Save high-resolution image with higher DPI for large datasets
dpi = 300 if len(data) > 5000 or len(data.columns) > 500 else 150
plt.savefig(args.output, bbox_inches='tight', pad_inches=0.5, format='png', dpi=dpi)
print(f"Heatmap saved to {args.output}")