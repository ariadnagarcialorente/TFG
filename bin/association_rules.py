import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

# Function to analyze association rules from binary data
def analyze_binary_association_rules(binary_df, min_support=0.1, min_threshold=0.7):
    # Find frequent itemsets
    frequent_itemsets = apriori(binary_df, min_support=min_support, use_colnames=True)
    
    # Generate association rules
    rules_df = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)
    
    return rules_df

# Function to visualize association rules
def visualize_rules(rules_df,image):    
    # Heatmap of lift values for top rules
    if len(rules_df) > 10:
        top_rules = rules_df.sort_values('lift', ascending=False).head(10)
    else:
        top_rules = rules_df.sort_values('lift', ascending=False)
    
    ## Create readable labels like: "['milk'] → ['bread']" for each rule
    labels = []
    for index, row in top_rules.iterrows():
        antecedent = list(row['antecedents'])  # Items on the left-hand side of the rule
        consequent = list(row['consequents'])  # Items on the right-hand side of the rule
        label = f"{antecedent} → {consequent}"
        labels.append(label)

    # Set up the figure size dynamically based on number of rules
    plt.figure(figsize=(12, len(labels) * 0.5 + 2))

    # Create a horizontal bar chart showing lift for each rule
    sns.barplot(
        x='lift',               
        y=np.arange(len(labels)),
        data=top_rules,         
        orient='h'              
    )

    plt.yticks(np.arange(len(labels)), labels)

    # Add a title and adjust layout
    plt.title('Top Association Rules by Lift')
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(image)


# Function to analyze real-world binary data
def analyze_real_data(file_path, min_support=0.1, min_confidence=0.5, image="association_rules.png"):
    # Load data
    data = pd.read_csv(file_path)
    
    # Check if data is binary
    if not np.all((data.values == 0) | (data.values == 1)):
        print("Warning: Data contains non-binary values. Converting to binary (missing value becomes 1).")
        data = (data.isna()).astype(int)
    
    total_ones = data.values.sum()
    total_elements = data.shape[0] * data.shape[1]
    percentage = total_ones / total_elements

    print(f"Loaded data with {data.shape[0]} rows and {data.shape[1]} columns. Number of 1s: {total_ones}. % = {percentage:.2%}")

    # Find association rules
    rules = analyze_binary_association_rules(data, min_support, min_confidence)
    

    print(f"Found {len(rules)} association rules.")
    readable_rules = rules.copy()
    readable_rules["antecedents"] = readable_rules["antecedents"].apply(lambda x: list(x))
    readable_rules["consequents"] = readable_rules["consequents"].apply(lambda x: list(x))
    
    columns_to_show = ['antecedents', 'consequents', 'support', 'confidence', 'lift']
    print(readable_rules[columns_to_show].sort_values('lift', ascending=False).head(15).to_string())
    
    # Visualize
    visualize_rules(rules,image)

    return rules, data
    
def main():
    parser = argparse.ArgumentParser(
        description="Analyze association rules from binary transaction data."
    )
    # Required arguments
    parser.add_argument(
        "input_file",
        help="Path to input CSV file containing binary transaction data"
    )
    parser.add_argument(
        "--min_support",
        type=float,
        default=0.1008,
        help="Minimum support threshold (default: 0.15)"
    )
    parser.add_argument(
        "--min_confidence",
        type=float,
        default=1,
        help="Minimum confidence threshold (default: 0.9)"
    )
    parser.add_argument(
        "--output",
        default="association_rules.csv",
        help="Output filename for rules (default: association_rules.csv)"
    )
    parser.add_argument(
        "--image",
        default="association_rules.png",
        help="Image filename for rules (default: association_rules.png)"
    )
    
    args = parser.parse_args()
    
    # Execute analysis pipeline
    rules, data = analyze_real_data(
        file_path=args.input_file,
        min_support=args.min_support,
        min_confidence=args.min_confidence,
        image = args.image
    )
    
    # Save results if rules were found
    if rules is not None and not rules.empty:
        rules.to_csv(args.output, index=False)
        print(f"\nSaved {len(rules)} rules to {args.output}")

main()