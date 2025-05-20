# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def clean_dataset(filepath, min_rows=0, min_percent=0, important_cols=None, imp_weight=1.0):
    # Load the dataset with missing values
    data = pd.read_csv(filepath)
    
    # Store original row count
    original_rows = data.shape[0]
    print(f"Dataset shape: {data.shape}")
    print(f"Available columns: {list(data.columns)}")
    
    # Calculate weighted missing value counts
    if important_cols and imp_weight > 1.0:
        # Create a weighted na_count where important columns count more
        other_cols = [col for col in data.columns if col not in important_cols]
        
        # Calculate missing values with weights
        important_na = data[important_cols].isna().sum(axis=1) * imp_weight
        other_na = data[other_cols].isna().sum(axis=1)
        data['na_count'] = important_na + other_na
        
        print(f"Important columns weighted {imp_weight}x: {important_cols}")
    else:
        # Simple count of missing values per row
        data['na_count'] = data.isna().sum(axis=1)
    
    # Sort by missing value count (most missing first)
    data = data.sort_values(by='na_count', ascending=False)
    
    # Remove rows with most missing values until threshold is reached
    while (data.shape[0] > min_rows) or (100 * data.shape[0] / original_rows > min_percent) and data.isnull().values.any():
        data = data.iloc[1:]
    
    # Report which threshold was reached
    if (data.shape[0] <= min_rows and (100 * data.shape[0] / original_rows <= min_percent)) or not data.isnull().values.any():
        print(f'Program ended successfully: {data.shape[0]}')
    elif data.shape[0] <= min_rows:
        # We hit the minimum rows constraint but the percentage is too low
        current_percent = 100 * data.shape[0] / original_rows
        print(f'Minimum number of rows reached, percent of rows too low: {data.shape[0]}')
        print(f'Recommended minimum percent of rows: {current_percent:.1f}%')
    else:
        # We hit the minimum percentage constraint but the number of rows is too low
        current_rows = data.shape[0]
        print(f'Minimum percent of rows reached, number of rows too low: {data.shape[0]}')
        print(f'Recommended minimum of rows: {current_rows}')
    
    # Drop the 'na_count' column (as it's no longer needed)
    data = data.drop(columns=['na_count'])

    data.to_csv('cleaned_dataset.csv', index=False)
    
    return data

def algorithm0_0():
    # Get user input for parameters
    filepath = input("Enter the dataset filepath (default: output_erased_dataset.csv): ") or 'output_erased_dataset.csv'
    min_rows = int(input("Indicate the minimum number of rows: "))
    min_percent = int(input("Indicate the minimum percent of rows: "))
    
    # Get important columns
    important = input("Enter important columns (comma-separated), or leave blank: ")
    important_cols = [c.strip() for c in important.split(',') if c.strip()] if important else []
    
    # Get importance weight if we have important columns
    imp_weight = 1.0
    if important_cols:
        imp_weight = float(input("Enter penalty weight for missing in important columns (e.g. 2.0): "))
    
    # Clean the dataset
    cleaned_data = clean_dataset(filepath, min_rows, min_percent, important_cols, imp_weight)
    
    # Save the cleaned dataset
    print(f"Cleaned dataset saved to 'cleaned_dataset.csv' with {cleaned_data.shape[0]} rows")

algorithm0_0()