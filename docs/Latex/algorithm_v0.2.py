import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Data cleaning with column importance weighting')
    parser.add_argument('--input', type=str, default='output_erased_dataset.csv',
                      help='Input CSV file path')
    parser.add_argument('--output', type=str, default='cleaned_dataset.csv',
                      help='Output CSV file path')
    parser.add_argument('-p','--percentile', type=int, default=75.0,
                      help='Missing values percentile threshold (0-100)')
    parser.add_argument('--image', type=str, default='missing_distribution.png',
                      help='Path for saving distribution plot')
    parser.add_argument('-c', '--important-cols', default='',
                      help='Comma-separated list of important columns')
    parser.add_argument('-w', '--importance-weight', type=float, default=1.0,
                      help='Weight multiplier for important column missing values')

    args = parser.parse_args()

    # Load and validate data
    data = pd.read_csv(args.input)
    original_cols = set(data.columns)
    
    # Process important columns
    important_cols = [col.strip() for col in args.important_cols.split(',') if col.strip()]
    important_cols = list(dict.fromkeys(important_cols))  # Remove duplicates
    
    if important_cols:
        missing = list(set(important_cols) - original_cols)
        if missing:
            raise ValueError(f"Missing important columns in dataset: {missing}")

    # Calculate weighted missing values
    if important_cols and args.importance_weight > 1.0:
        other_cols = [col for col in data.columns if col not in important_cols]
        data['na_count'] = (data[important_cols].isna().sum(axis=1) * args.importance_weight + data[other_cols].isna().sum(axis=1))
        print(f"Applying {args.importance_weight}x weight to important columns: {important_cols}")
    else:
        data['na_count'] = data.isna().sum(axis=1)
        if important_cols:
            print("Using standard weighting (importance weight <= 1.0)")

    # Generate distribution visualization
    plt.figure(figsize=(10, 6))
    sns.histplot(data['na_count'], bins=30, kde=True)
    plt.title(f'Missing Values Distribution ({"Weighted" if important_cols else "Standard"})')
    plt.xlabel('Weighted Missing Count')
    plt.ylabel('Frequency')
    plt.grid(True)
    plt.savefig(args.image)
    plt.close()

    # Apply percentile filtering
    threshold = data['na_count'].quantile(args.percentile / 100)
    filtered = data[data['na_count'] <= threshold].copy()
    filtered.drop(columns=['na_count'], inplace=True)
    
    # Save and report results
    filtered.to_csv(args.output, index=False)
    print(f"\nDataset cleaned: {len(data) - len(filtered)} rows removed")
    print(f"Final dataset size: {len(filtered)} rows")
    print(f"Threshold: {threshold:.2f} weighted missing values")
    print(f"Results saved to {os.path.abspath(args.output)}")
    print(f"Distribution plot saved to {os.path.abspath(args.image)}")

main()
