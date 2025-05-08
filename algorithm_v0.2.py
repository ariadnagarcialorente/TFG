# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset with missing values
data = pd.read_csv('output_erased_dataset.csv')

# Calculate number of missing values per row
data['na_count'] = data.isna().sum(axis=1)

# Display distribution of missing values per row
plt.figure(figsize=(10, 6))
sns.histplot(data['na_count'], bins=30, kde=True)
plt.title('Distribution of Missing Values per Row')
plt.xlabel('Number of Missing Values')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

# Ask user for percentile threshold (e.g., keep rows below 75th percentile of missing counts)
percentile_threshold = float(input("Enter the percentile (0-100) of missing values per row to keep (e.g., 75): "))
threshold_value = data['na_count'].quantile(percentile_threshold / 100)

# Filter the dataset based on distribution threshold
filtered_data = data[data['na_count'] <= threshold_value].copy()

print(f"Filtered {data.shape[0] - filtered_data.shape[0]} rows with high missingness (above {percentile_threshold}th percentile).")
print(f"Remaining rows: {filtered_data.shape[0]}")

# Drop the 'na_count' column
filtered_data = filtered_data.drop(columns=['na_count'])

# Save the cleaned dataset
filtered_data.to_csv('cleaned_dataset.csv', index=False)