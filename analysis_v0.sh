#!/bin/bash

# Script to execute 4 Python algorithm versions, time them, and compare missing numbers

echo "Algorithm Performance Comparison"
echo "===============================\n"

# Function to count missing numbers by comparing two files
count_missing_numbers() {
    output_file=$1
    cleaned_file=$2
    
    # Check if both files exist
    if [ ! -f "$output_file" ] || [ ! -f "$cleaned_file" ]; then
        echo "Error: One or both files not found."
        return 1
    fi
    
    # Count missing numbers by comparing files
    # This uses awk to count lines in cleaned_dataset that aren't in output_erased_dataset
    missing_count=$(awk 'NR==FNR{a[$0];next} !($0 in a)' "$output_file" "$cleaned_file" | wc -l)
    
    echo "$missing_count"
}

source env/bin/activate

# Results table header
printf "%-15s %-15s %-25s\n" "Algorithm" "Time (sec)" "Missing Numbers"
printf "%-15s %-15s %-25s\n" "----------" "----------" "--------------"

# Loop through the 4 algorithm versions
for version in {0..3}; do
    algorithm_file="algorithm_v0.${version}.py"
    
    # Check if algorithm file exists
    if [ ! -f "$algorithm_file" ]; then
        echo "Error: $algorithm_file not found."
        continue
    fi
    
    echo "Executing $algorithm_file..."
    
    # Time the execution of the algorithm
    start_time=$(date +%s.%N)
    python3 "$algorithm_file"
    end_time=$(date +%s.%N)
    
    # Calculate execution time
    execution_time=$(echo "$end_time - $start_time" | bc)
    
    # Count missing numbers
    missing_numbers=$(count_missing_numbers "output_erased_dataset.csv" "cleaned_dataset.csv")
    
    # Print results
    printf "%-15s %-15.4f %-25s\n" "v0.${version}" "$execution_time" "$missing_numbers"
    
    # Small separator between runs
    echo "---------------------------------------"
done

echo "\nComparison completed!"