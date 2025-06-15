import pandas as pd
import numpy as np

# Create datasets for 100/100 score (Pair 1)
print("Creating datasets for 100/100 score...")

# Pair 1: Perfect Score (100/100)
# Complete dataset - no missing values
complete_perfect = pd.DataFrame({
    'id': range(1, 1001),
    'name': [f'Person_{i}' for i in range(1, 1001)],
    'age': np.random.randint(18, 80, 1000),
    'salary': np.random.randint(30000, 120000, 1000),
    'department': np.random.choice(['IT', 'HR', 'Finance', 'Marketing'], 1000),
    'important_col_1': np.random.randint(1, 100, 1000),
    'important_col_2': np.random.randint(1, 100, 1000),
    'extra_col_1': np.random.random(1000),
    'extra_col_2': np.random.random(1000),
    'extra_col_3': np.random.random(1000)
})

# Erased dataset - introduce missing values
erased_perfect = complete_perfect.copy()
# Add 200 missing values randomly distributed
missing_positions = np.random.choice(erased_perfect.size, 200, replace=False)
erased_flat = erased_perfect.values.flatten()
erased_flat[missing_positions] = np.nan
erased_perfect = pd.DataFrame(erased_flat.reshape(erased_perfect.shape), 
                             columns=erased_perfect.columns)

# Cleaned dataset - perfect cleaning (removes all missing, keeps all constraints)
cleaned_perfect = complete_perfect.copy()  # Perfect cleaning = original complete data

# Save perfect score datasets
complete_perfect.to_csv('complete_perfect.csv', index=False)
erased_perfect.to_csv('erased_perfect.csv', index=False)
cleaned_perfect.to_csv('cleaned_perfect.csv', index=False)

print("Perfect score datasets created!")
print(f"Complete: {len(complete_perfect)} rows, {len(complete_perfect.columns)} columns")
print(f"Erased: {len(erased_perfect)} rows, {len(erased_perfect.columns)} columns, {erased_perfect.isna().sum().sum()} missing")
print(f"Cleaned: {len(cleaned_perfect)} rows, {len(cleaned_perfect.columns)} columns, {cleaned_perfect.isna().sum().sum()} missing")

print("\n" + "="*50 + "\n")

print("\nCommand line arguments for testing:")
print("\nFor 100/100 score:")
print("python score_calculator.py --complete complete_perfect.csv --erased erased_perfect.csv --cleaned cleaned_perfect.csv --min-rows 500 --min-percent 50.0 --max-missing 50 --col-threshold 5 --col-relative-threshold 50.0 --important-cols 'important_col_1,important_col_2'")

# --- continue from above ---

print("\nGenerating datasets for 0/100 score...")

# Pair 2: Guaranteed Zero Score (0/100)
# Build a small erased dataset with some missing values in important cols
erased_zero = pd.DataFrame({
    'important_col_1': [10, np.nan, 30],
    'important_col_2': [np.nan, 50, 60],
    'other_col':       [1, 2, np.nan]
})

# Build a cleaned dataset that drops all original columns entirely
# so every important column is considered “dropped” (max penalty)
cleaned_zero = pd.DataFrame()  # 0 rows × 0 cols

# Save zero‐score datasets
erased_zero.to_csv('erased_zero.csv', index=False)
cleaned_zero.to_csv('cleaned_zero.csv', index=False)

print("Zero score datasets created!")
print(f"Erased Zero: {len(erased_zero)} rows, {len(erased_zero.columns)} columns, {erased_zero.isna().sum().sum()} missing")
print(f"Cleaned Zero: {len(cleaned_zero)} rows, {len(cleaned_zero.columns)} columns, {cleaned_zero.isna().sum().sum()} missing\n")

print("For 0/100 score:")
print("python score_calculator.py \\")
print("  --complete complete_perfect.csv \\")
print("  --erased erased_zero.csv \\")
print("  --cleaned cleaned_zero.csv \\")
print("  --min-rows 1 \\")
print("  --min-percent 50.0 \\")
print("  --max-missing 0 \\")
print("  --col-threshold 1 \\")
print("  --col-relative-threshold 50.0 \\")
print("  --important-cols 'important_col_1,important_col_2'")
