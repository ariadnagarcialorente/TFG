import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

# Create dataset
data = {
    'A': [1, 2, 3, 4, 5],
    'B': [5, np.nan, 3, 2, 1],
    'C': [1, 2, np.nan, 4, 5],
    'D': [np.nan, 2, 3, 4, 5],
    'E': [1, 2, 3, np.nan, 5]
}
df = pd.DataFrame(data)

# Improved plotting function with size display
def plot_enhanced_heatmap(df, title, highlight_pair=None):
    plt.figure(figsize=(8, 4))
    cmap = ListedColormap(["#2ecc71", "#e74c3c"])  # Green = present, Red = missing
    
    # Plot missingness heatmap
    ax = sns.heatmap(
        df.isnull(), 
        cbar=False, 
        cmap=cmap, 
        yticklabels=True,
        linewidths=0.5,
        linecolor="lightgray"
    )
    
    # Highlight rows used for pairwise deletion
    if highlight_pair:
        col1, col2 = highlight_pair
        valid_rows = df[col1].notna() & df[col2].notna()
        rows_used = valid_rows.sum()  # Count of rows used for this pair
        for i, valid in enumerate(valid_rows):
            if valid:
                ax.add_patch(plt.Rectangle(
                    (0, i), 
                    len(df.columns), 
                    1, 
                    fill=False, 
                    edgecolor="blue", 
                    lw=2, 
                    clip_on=False
                ))
    else:
        rows_used = None
    
    # Create main title with dataset size subtitle
    total_rows = len(df)
    plt.suptitle(title, fontsize=14, y=0.97)
    
    # Create subtitle with row information
    if highlight_pair:
        subtitle = f"Total rows: {total_rows} | Rows used for {col1}-{col2}: {rows_used}"
    else:
        subtitle = f"Total rows: {total_rows}"
    
    plt.title(subtitle, fontsize=11, pad=12)
    
    plt.xlabel("Variables", fontsize=12)
    plt.ylabel("Rows", fontsize=12)
    
    # Add legend
    handles = [
        Patch(facecolor="#2ecc71", label="Data Present"),
        Patch(facecolor="#e74c3c", label="Missing"),
    ]
    if highlight_pair:
        handles.append(Patch(edgecolor="blue", facecolor="none", lw=2, label="Used in Pairwise"))
    plt.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc="upper left")
    
    plt.tight_layout()
    plt.savefig(title.replace(" ", "_").lower() + ".png", bbox_inches="tight")
    plt.show()

# Generate plots
plot_enhanced_heatmap(df, "Original Dataset")
listwise_df = df.dropna()
plot_enhanced_heatmap(listwise_df, "Listwise Deletion")
plot_enhanced_heatmap(df, "Pairwise Deletion (A vs B)", highlight_pair=("A", "B"))