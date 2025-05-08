import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
import matplotlib.pyplot as plt
import seaborn as sns

# Function to generate a sample binary matrix
def generate_binary_matrix(n_samples=1000, n_features=10, density=0.3):
    """
    Generate a sample binary matrix with specified dimensions and density.
    
    Parameters:
    -----------
    n_samples : int
        Number of samples (rows)
    n_features : int
        Number of features (columns)
    density : float
        Approximate density of 1's in the matrix (between 0 and 1)
        
    Returns:
    --------
    DataFrame with binary values
    """
    # Generate random binary matrix
    random_matrix = np.random.random((n_samples, n_features)) < density
    
    # Convert to DataFrame with named columns
    column_names = [f'feature_{i}' for i in range(n_features)]
    df = pd.DataFrame(random_matrix.astype(int), columns=column_names)
    
    return df

# Function to analyze association rules from binary data
def analyze_binary_association_rules(binary_df, min_support=0.1, min_threshold=0.7):
    """
    Analyze association rules from binary data.
    
    Parameters:
    -----------
    binary_df : DataFrame
        DataFrame containing binary data (0's and 1's)
    min_support : float
        Minimum support threshold for frequent itemsets
    min_threshold : float
        Minimum threshold for metrics (confidence by default)
        
    Returns:
    --------
    rules_df : DataFrame
        DataFrame containing association rules
    """
    # Find frequent itemsets
    frequent_itemsets = apriori(binary_df, min_support=min_support, use_colnames=True)
    
    # Generate association rules
    rules_df = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_threshold)
    
    return rules_df

# Function to visualize association rules
def visualize_rules(rules_df):
    """
    Create visualizations for association rules.
    
    Parameters:
    -----------
    rules_df : DataFrame
        DataFrame containing association rules
    """
    # Scatter plot of support vs confidence
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='support', y='confidence', size='lift', data=rules_df, sizes=(50, 200))
    plt.title('Support vs Confidence with Lift as Size')
    plt.grid(True)
    plt.show()
    
    # Heatmap of lift values for top rules
    if len(rules_df) > 10:
        top_rules = rules_df.sort_values('lift', ascending=False).head(10)
    else:
        top_rules = rules_df.sort_values('lift', ascending=False)
    
    # Format antecedents and consequents for display
    labels = [f"{str(row['antecedents'])} → {str(row['consequents'])}" for _, row in top_rules.iterrows()]
    
    plt.figure(figsize=(12, len(labels)*0.5 + 2))
    sns.barplot(x='lift', y=np.arange(len(labels)), data=top_rules, orient='h')
    plt.yticks(np.arange(len(labels)), labels)
    plt.title('Top Rules by Lift')
    plt.tight_layout()
    plt.show()


# Example usage
if __name__ == "__main__":
    # Generate sample binary data
    # You can replace this with your own binary matrix
    binary_data = generate_binary_matrix(n_samples=1000, n_features=8, density=0.3)
    
    print("Sample of binary data:")
    print(binary_data.head())
    
    # Calculate item frequencies (how often each feature is 1)
    item_frequencies = binary_data.mean().sort_values(ascending=False)
    print("\nFeature frequencies (proportion of 1's):")
    print(item_frequencies)
    
    # Analyze association rules
    rules = analyze_binary_association_rules(
        binary_data, 
        min_support=0.1,  # Items must appear in at least 10% of transactions
        min_threshold=0.5  # Rules must have at least 50% confidence
    )
    
    # Print the rules
    if len(rules) > 0:
        print("\nAssociation Rules:")
        # Format the rules for better readability
        readable_rules = rules.copy()
        readable_rules["antecedents"] = readable_rules["antecedents"].apply(lambda x: list(x))
        readable_rules["consequents"] = readable_rules["consequents"].apply(lambda x: list(x))
        
        # Select important columns and sort by lift
        columns_to_show = ['antecedents', 'consequents', 'support', 'confidence', 'lift']
        print(readable_rules[columns_to_show].sort_values('lift', ascending=False).to_string())
        
        # Visualize the rules
        visualize_rules(rules)
    else:
        print("\nNo rules found with the specified thresholds. Try lowering min_support or min_threshold.")
    
    # Example of analyzing specific relationships between 0 and 1 values
    print("\nAnalyzing specific 0-1 relationships:")
    
    # Convert to explicit 0/1 representation to analyze relationships between 0s and 1s
    # This creates new columns for each feature_i_value (where value is 0 or 1)
    binary_explicit = pd.DataFrame()
    for col in binary_data.columns:
        binary_explicit[f"{col}_1"] = binary_data[col]
        binary_explicit[f"{col}_0"] = 1 - binary_data[col]
    
    # Remove columns with all zeros (these would cause errors in apriori)
    binary_explicit = binary_explicit.loc[:, binary_explicit.sum() > 0]
    
    # Now run association rules on the explicit 0/1 representation
    print("Sample of explicit 0/1 representation:")
    print(binary_explicit.head())
    
    # Analyze association rules
    explicit_rules = analyze_binary_association_rules(
        binary_explicit, 
        min_support=0.2,  # Higher support threshold due to more features
        min_threshold=0.6
    )
    
    # Print the rules
    if len(explicit_rules) > 0:
        print("\nAssociation Rules between 0s and 1s:")
        # Format the rules for better readability
        readable_explicit_rules = explicit_rules.copy()
        readable_explicit_rules["antecedents"] = readable_explicit_rules["antecedents"].apply(lambda x: list(x))
        readable_explicit_rules["consequents"] = readable_explicit_rules["consequents"].apply(lambda x: list(x))
        
        # Select important columns and sort by lift
        columns_to_show = ['antecedents', 'consequents', 'support', 'confidence', 'lift']
        print(readable_explicit_rules[columns_to_show].sort_values('lift', ascending=False).head(15).to_string())
    else:
        print("\nNo explicit 0/1 rules found with the specified thresholds. Try adjusting parameters.")

# Function to analyze real-world binary data
def analyze_real_data(file_path, delimiter=',', min_support=0.1, min_confidence=0.5):
    """
    Analyze association rules from a real-world binary dataset.
    
    Parameters:
    -----------
    file_path : str
        Path to the CSV file containing binary data
    delimiter : str
        Delimiter used in the CSV file
    min_support : float
        Minimum support threshold for frequent itemsets
    min_confidence : float
        Minimum confidence threshold for rules
    """
    try:
        # Load data
        data = pd.read_csv(file_path, delimiter=delimiter)
        
        # Check if data is binary
        if not all((data.values == 0) | (data.values == 1) | pd.isna(data.values)):
            print("Warning: Data contains non-binary values. Converting to binary (>0 becomes 1).")
            data = (data > 0).astype(int)
        
        # Handle missing values
        if data.isna().any().any():
            print("Warning: Data contains missing values. Filling with 0.")
            data = data.fillna(0)
        
        print(f"Loaded data with {data.shape[0]} rows and {data.shape[1]} columns.")
        
        # Find association rules
        rules = analyze_binary_association_rules(data, min_support, min_confidence)
        
        # Output results
        if len(rules) > 0:
            print(f"Found {len(rules)} association rules.")
            readable_rules = rules.copy()
            readable_rules["antecedents"] = readable_rules["antecedents"].apply(lambda x: list(x))
            readable_rules["consequents"] = readable_rules["consequents"].apply(lambda x: list(x))
            
            columns_to_show = ['antecedents', 'consequents', 'support', 'confidence', 'lift']
            print(readable_rules[columns_to_show].sort_values('lift', ascending=False).head(15).to_string())
            
            # Visualize
            visualize_rules(rules)
        else:
            print("No rules found with the specified thresholds.")
        
        return rules, data
    
    except Exception as e:
        print(f"Error analyzing data: {e}")
        return None, None

# Example usage for real data:
# rules, data = analyze_real_data("your_binary_data.csv", delimiter=',', min_support=0.1, min_confidence=0.5)