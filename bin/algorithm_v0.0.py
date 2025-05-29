# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def clean_dataset(filepath, output_filepath, min_rows=0, min_percent=0, important_cols=None, imp_weight=1.0):
    # Load the dataset with missing values
    data = pd.read_csv(filepath)
    
    # Store original row count
    original_rows = data.shape[0]

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

    data.to_csv(output_filepath, index=False)
    
    return data

def algorithm0_0():
    parser = argparse.ArgumentParser(
        description="Clean dataset by removing rows with missing values based on specified thresholds."
    )
    parser.add_argument(
        "--input", "-i",
        default="output_erased_dataset.csv",
        help="Path to input CSV file (default: output_erased_dataset.csv)"
    )
    parser.add_argument(
        "--min-rows", "-r",
        type=int,
        default=0,
        required=True,
        help="Minimum number of rows to keep (default: 0)"
    )
    parser.add_argument(
        "--min-percent", "-p",
        type=float,
        default=0,
        required=True,
        help="Minimum percentage of original rows to keep (default: 0)"
    )
    parser.add_argument(
        "--important-cols", "-c",
        default="",
        help="Comma-separated list of important columns (default: none)"
    )
    parser.add_argument(
        "--importance-weight", "-w",
        type=float,
        default=1.0,
        help="Weight for missing values in important columns (default: 1.0)"
    )
    parser.add_argument(
        "--output", "-o",
        default="input_cleaned.csv",
        help="Path for output CSV file (default: input_cleaned.csv)"
    )

    args = parser.parse_args()
    filepath = args.input
    output_filepath = args.output
    min_rows = args.min_rows
    min_percent = args.min_percent
    important_cols = [c.strip() for c in args.important_cols.split(',') if c.strip()] if args.important_cols else []
    imp_weight = args.importance_weight
    # Clean the dataset
    cleaned_data = clean_dataset(filepath, output_filepath, min_rows, min_percent, important_cols, imp_weight)
    
    # Save the cleaned dataset
    print(f"Cleaned dataset saved to 'cleaned_dataset.csv' with {cleaned_data.shape[0]} rows")

algorithm0_0()