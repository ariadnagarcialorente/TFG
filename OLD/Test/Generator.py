import pandas as pd
import numpy as np

# Test Case 1: All rows have 100% missing values
def test_case_1():
    rows = 500
    cols = 10
    data = pd.DataFrame(np.nan, index=range(rows), columns=[f'col_{i}' for i in range(cols)])
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 2: No missing values
def test_case_2():
    rows = 1000
    cols = 10
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 3: Uniform sparse missingness
def test_case_3():
    rows = 1000
    cols = 10
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    for i in range(rows):
        col_idx = np.random.randint(0, cols)
        data.iloc[i, col_idx] = np.nan
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 4: Dense block missingness
def test_case_4():
    rows = 1000
    cols = 20
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    for i in range(200):
        col_indices = np.random.choice(cols, 10, replace=False)
        data.iloc[i, col_indices] = np.nan
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 5: 1000 rows, 1 missing value per row
def test_case_5():
    rows = 1000
    cols = 10
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    for i in range(rows):
        col_idx = np.random.randint(0, cols)
        data.iloc[i, col_idx] = np.nan
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 6: All rows have ≤5 missing values
def test_case_6():
    rows = 200
    cols = 20
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    for i in range(rows):
        num_missing = np.random.randint(1, 6)
        col_indices = np.random.choice(cols, num_missing, replace=False)
        data.iloc[i, col_indices] = np.nan
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 7: Empty CSV file
def test_case_7():
    cols = 10
    data = pd.DataFrame(columns=[f'col_{i}' for i in range(cols)])
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, 0, cols

# Test Case 8: Single row with 100% missingness
def test_case_8():
    rows = 1000
    cols = 10
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    data.iloc[0, :] = np.nan
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 9: 1 row with 1000 missing values
def test_case_9():
    rows = 1000
    cols = 1000
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    data.iloc[0, :] = np.nan
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 10: All rows complete
def test_case_10():
    rows = 1000
    cols = 10
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Test Case 11: Conflicting Constraints
def test_case_11():
    rows = 500
    cols = 10
    data = pd.DataFrame(np.random.rand(rows, cols), columns=[f'col_{i}' for i in range(cols)])
    for i in range(rows):
        col_indices = np.random.choice(cols, 2, replace=False)
        data.iloc[i, col_indices] = np.nan
    data.to_csv('output_erased_dataset.csv', index=False)
    return data, rows, cols

# Function to generate CSVs for all test cases
def generate_all_csvs():
    
    # Dictionary of all test case functions
    test_cases = {
        1: test_case_1,
        2: test_case_2,
        3: test_case_3,
        4: test_case_4,
        5: test_case_5,
        6: test_case_6,
        7: test_case_7,
        8: test_case_8,
        9: test_case_9,
        10: test_case_10,
        11: test_case_11
    }
    
    # Generate all the CSVs
    results = {}
    for case_num, test_func in test_cases.items():
        data, rows, cols = test_func()
        missing_count = data.isna().sum().sum()
        missing_percent = 0 if rows*cols == 0 else missing_count / (rows * cols) * 100
        
        # Store results
        results[case_num] = {
            "rows": rows,
            "cols": cols,
            "missing_count": int(missing_count),
            "missing_percent": round(missing_percent, 2),
            "file_name": f"test_case_{case_num}.csv"
        }
    
    return results

# Run the generator
test_results = test_case_3()
