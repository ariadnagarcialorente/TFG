# Import required libraries
import pandas as pd

# Load the dataset
data = pd.read_csv('output_erased_dataset.csv')

# Calculate missing values per row
data['na_count'] = data.isna().sum(axis=1)

# Sort rows by missing count (descending)
data_sorted = data.sort_values('na_count', ascending=False).reset_index(drop=True)

# Get user inputs for all criteria
percentile = float(input("Enter percentile threshold for row missingness (0-100): "))
min_rows = int(input("Minimum absolute rows to keep: "))
min_percent = float(input("Minimum percentage of rows to keep (0-100): "))
max_total_missing = int(input("Maximum total missing values allowed: "))

# Calculate percentile-based threshold
threshold_value = data['na_count'].quantile(percentile / 100)

# Precompute critical values for optimization
original_row_count = len(data_sorted)
reverse_cumsum = data_sorted['na_count'][::-1].cumsum()[::-1].values
max_na_values = data_sorted['na_count'].values

# Track best solution across iterations
best_removal_point = 0
max_conditions_met = -1

for removal_point in range(0, original_row_count + 1):
    if removal_point < len(reverse_cumsum):
        current_total_missing = reverse_cumsum[removal_point]
        current_max_na = max_na_values[removal_point] if removal_point < len(max_na_values) else 0
    else:
        current_total_missing = 0
        current_max_na = 0
    
    remaining_rows = original_row_count - removal_point
    remaining_percent = (remaining_rows / original_row_count) * 100

    # Evaluate all criteria
    conditions = [
        remaining_rows >= min_rows,
        remaining_percent >= min_percent,
        current_total_missing <= max_total_missing,
        current_max_na <= threshold_value
    ]
    conditions_met = sum(conditions)

    # Update best solution (prefer earlier removal points if tied)
    if conditions_met > max_conditions_met or \
       (conditions_met == max_conditions_met and removal_point < best_removal_point):
        max_conditions_met = conditions_met
        best_removal_point = removal_point

    # Early exit if all conditions met
    if conditions_met == 4:
        break

# Apply optimal filtering
filtered_data = data_sorted.iloc[best_removal_point:].copy()
rows_removed = best_removal_point

# Cleanup and save
filtered_data.drop('na_count', axis=1, inplace=True)
filtered_data.to_csv('cleaned_dataset.csv', index=False)

# Generate report
print(f"\nOptimization Complete!")
print(f"Rows removed: {rows_removed}")
print(f"Final row count: {len(filtered_data)}")
print(f"Conditions satisfied: {max_conditions_met}/4")
print(f"Total missing values: {current_total_missing}")
print(f"Highest row missingness: {current_max_na}")