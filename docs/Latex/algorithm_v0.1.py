import argparse
import pandas as pd

def clean_dataset(filepath, min_rows=0, min_percent=0.0, max_missing=0, important_cols=None, imp_weight=1.0):
    # Load the dataset
    data = pd.read_csv(filepath)
    original_rows = data.shape[0]

    # Fill important_cols if empty
    if important_cols is None:
        important_cols = []

    # Identify other columns
    other_cols = [c for c in data.columns if c not in important_cols]

    # Compute two columns per row:
    # - na_total: raw missing value count
    # - na_weighted: weighted score for sorting
    data['na_total'] = data.isna().sum(axis=1)

    if important_cols and imp_weight > 1.0:
        imp_na = data[important_cols].isna().sum(axis=1)
        oth_na = data[other_cols].isna().sum(axis=1)
        data['na_weighted'] = imp_na * imp_weight + oth_na
        print(f"Applied weight {imp_weight} to columns: {important_cols}")
    else:
        data['na_weighted'] = data['na_total']

    # Sort by descending na_weighted to remove worst rows first
    data = data.sort_values(by='na_weighted', ascending=False)

    # Iteratively drop worst rows until all criteria are met
    # Iteratively drop worst rows until all criteria are met
    while True:
        total_missing = data['na_total'].sum()
        row_count = data.shape[0]
        percent_retained = 100 * row_count / original_rows if original_rows else 0

        # Debug
        #print(f"Rows remaining: {row_count}, Total missing: {total_missing}, Percent retained: {percent_retained:.2f}%")

        if (
            total_missing <= max_missing or
            row_count < min_rows or
            percent_retained <= min_percent
        ):
            break

        if data.empty:
            break

        # Drop worst row
        data = data.iloc[1:]


    # Final output
    current_rows = data.shape[0]
    current_percent = 100 * current_rows / original_rows if original_rows else 0
    current_missing = data['na_total'].sum()

    if current_missing == 0:
        print(f"Success: no missing values remain ({current_rows} rows)")
    elif (
        current_rows < min_rows and
        current_percent <= min_percent and
        current_missing <= max_missing
    ):
        print(f"Success: thresholds met ({current_rows} rows, {current_percent:.1f}%, {current_missing} missing values)")
    else:
        print("Thresholds not fully met.")
        if current_rows > min_rows:
            print(f"  Rows: {current_rows} < {min_rows}")
        if current_percent > min_percent:
            print(f"  Percent: {current_percent:.1f}% < {min_percent}%")
        if current_missing > max_missing:
            print(f"  Total missing: {current_missing} > {max_missing}")

    # Drop weighted column if you don’t want it in the output
    result = data.drop(columns=['na_weighted', 'na_total'])
    return result



def main():
    parser = argparse.ArgumentParser(
        description="Remove rows based on missing-data thresholds."
    )
    parser.add_argument('-i', '--input', default='output_erased_dataset.csv', help='Input CSV file path')
    parser.add_argument('-r', '--min-rows', type=int, default=0, help='Minimum rows to keep')
    parser.add_argument('-p', '--min-percent', type=float, default=0.0, help='Minimum percent of original rows to keep')
    parser.add_argument('-m', '--max-missing', type=int, default=0, help='Maximum missing values per row allowed')
    parser.add_argument('-c', '--important-cols', default='', help='Comma-separated important columns')
    parser.add_argument('-w', '--importance-weight', type=float, default=1.0, help='Weight for important-col missing')
    parser.add_argument('-o', '--output', default='cleaned_dataset.csv', help='Output CSV file path')

    args = parser.parse_args()
    cols = [x.strip() for x in args.important_cols.split(',') if x.strip()]
    df = clean_dataset(
        filepath=args.input,
        min_rows=args.min_rows,
        min_percent=args.min_percent,
        max_missing=args.max_missing,
        important_cols=cols,
        imp_weight=args.importance_weight
    )
    df.to_csv(args.output, index=False)
    print(f"Result saved to {args.output} with {df.shape[0]} rows.")

if __name__ == '__main__':
    main()
