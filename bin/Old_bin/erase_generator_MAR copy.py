import pandas as pd
import numpy as np
import random



def delete_MAR_1_to_x(data, x_vars, target_var=None, p_miss=0.2, seed=None):

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mar = data.copy()
    
    # Identify the target variable if not specified
    if target_var is None:
        target_var = [col for col in data.columns if col not in x_vars][0] if x_vars else data.columns[0]
    
    # Create a probability of missingness based on x_vars
    if len(x_vars) > 0:
        # Initialize probabilities
        probs = np.zeros(len(data))
        
        for var in x_vars:
            if var in data.columns:
                if pd.api.types.is_numeric_dtype(data[var]):
                    # For numeric variables, use normalized values
                    var_values = data[var].values
                    if not all(pd.isna(var_values)) and np.nanmax(var_values) > np.nanmin(var_values):
                        normalized = (var_values - np.nanmin(var_values)) / (np.nanmax(var_values) - np.nanmin(var_values))
                        probs += normalized
                else:
                    # For categorical variables, use frequency-based approach
                    # Less frequent categories have higher probability
                    value_counts = data[var].value_counts(normalize=True)
                    cat_probs = np.array([1 - value_counts.get(val, 0) for val in data[var]])
                    cat_probs = cat_probs / cat_probs.max() if cat_probs.max() > 0 else cat_probs
                    probs += cat_probs
        
        # Normalize the sum of probabilities
        if np.nanmax(probs) > np.nanmin(probs):
            probs = (probs - np.nanmin(probs)) / (np.nanmax(probs) - np.nanmin(probs))
            
            # Adjust probabilities to achieve desired missingness rate
            probs = probs * p_miss * 2  # Scale to have average close to p_miss
        else:
            # If all values are the same, use uniform probability
            probs = np.ones(len(data)) * p_miss
    else:
        # If no x_vars are provided, use uniform probability
        probs = np.ones(len(data)) * p_miss
    
    # Cap probabilities at 1
    probs = np.minimum(probs, 1)
    
    # Determine which values will be missing
    missing_mask = np.random.random(len(data)) < probs
    
    # Set values to missing
    data_mar.loc[missing_mask, target_var] = np.nan
    
    return data_mar


def delete_MAR_censoring(data, x_var, target_var=None, p_miss=0.2, censoring_tail="right", seed=None):

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mar = data.copy()
    
    # Determine target variable if not specified
    if target_var is None:
        target_var = [col for col in data.columns if col != x_var][0]
    
    # Create probability of missing based on x_var
    if pd.api.types.is_numeric_dtype(data[x_var]):
        # For numeric variables, use rank-based approach
        x_values = data[x_var].values
        
        # Create probability of missing based on x_var
        if censoring_tail == "right":
            # Higher values of x_var have higher probability of missing
            probs = stats.rankdata(x_values) / len(x_values)
        else:  # "left"
            # Lower values of x_var have higher probability of missing
            probs = 1 - (stats.rankdata(x_values) / len(x_values))
    else:
        # For categorical variables, use frequency-based approach
        value_counts = data[x_var].value_counts(normalize=True)
        value_counts_sorted = value_counts.sort_values(ascending=True if censoring_tail == "right" else False)
        
        # Map categories to probabilities based on their frequency
        cat_to_prob = {}
        for i, (cat, _) in enumerate(value_counts_sorted.items()):
            cat_to_prob[cat] = (i + 1) / len(value_counts_sorted)
        
        # Assign probabilities to each row
        probs = np.array([cat_to_prob.get(val, 0.5) for val in data[x_var]])
    
    # Adjust probabilities to achieve desired missingness rate
    probs = probs * p_miss * 2  # Scale to have average close to p_miss
    
    # Cap probabilities at 1
    probs = np.minimum(probs, 1)
    
    # Determine which values will be missing
    missing_mask = np.random.random(len(data)) < probs
    
    # Set values to missing
    data_mar.loc[missing_mask, target_var] = np.nan
    
    return data_mar


def delete_MAR_one_group(data, group_var, target_var=None, p_miss=0.2, group_val=None, seed=None):

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mar = data.copy()
    
    # Determine target variable if not specified
    if target_var is None:
        target_var = [col for col in data.columns if col != group_var][0]
    
    # Determine group value if not specified
    if group_val is None:
        group_val = data[group_var].value_counts().index[0]
    
    # Create mask for the specified group
    group_mask = data[group_var] == group_val
    
    # Calculate how many values to delete to achieve p_miss overall
    n_missing = int(p_miss * len(data))
    
    # If the group has fewer values than n_missing, adjust n_missing
    if sum(group_mask) < n_missing:
        n_missing = sum(group_mask)
    
    # Randomly select indices to set to missing within the group
    indices_in_group = np.where(group_mask)[0]
    if len(indices_in_group) > 0:
        missing_indices = np.random.choice(indices_in_group, size=n_missing, replace=False)
        data_mar.loc[missing_indices, target_var] = np.nan
    
    return data_mar


def delete_MAR_rank(data, x_var, target_var=None, p_miss=0.2, seed=None):

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mar = data.copy()
    
    # Determine target variable if not specified
    if target_var is None:
        target_var = [col for col in data.columns if col != x_var][0]
    
    if pd.api.types.is_numeric_dtype(data[x_var]):
        # For numeric variables, use traditional ranking
        ranks = stats.rankdata(data[x_var].values)
        probs = ranks / len(data)
    else:
        # For categorical variables, assign ranks based on frequency
        # Less frequent categories get higher ranks (more likely to be missing)
        value_counts = data[x_var].value_counts(normalize=True)
        
        # Create a mapping from category to rank
        cat_ranks = {}
        for i, (cat, freq) in enumerate(value_counts.sort_values(ascending=False).items()):
            cat_ranks[cat] = (i + 1) / len(value_counts)
        
        # Assign probabilities based on category ranks
        probs = np.array([cat_ranks.get(val, 0.5) for val in data[x_var]])
    
    # Adjust probabilities to achieve desired missingness rate
    probs = probs * p_miss * 2  # Scale to have average close to p_miss
    
    # Cap probabilities at 1
    probs = np.minimum(probs, 1)
    
    # Determine which values will be missing
    missing_mask = np.random.random(len(data)) < probs
    
    # Set values to missing
    data_mar.loc[missing_mask, target_var] = np.nan
    
    return data_mar



# Get user input for percentage of data to erase
Percent = float(input("Insert a percentage between 0 and 100 to be erased: "))

# Load dataset from CSV file
data = pd.read_csv('output_complete_dataset.csv')

"""
REMEMBER THE FUNCTION
"""
    
# Convert to DataFrame (note: this step is redundant as data is already a DataFrame)
df = pd.DataFrame(data)

# Display first 5 rows of modified data
print(df.head())

# Save modified dataset to new CSV file
df.to_csv('output_erased_dataset.csv', index=False)

# Confirm completion
print("Complete DataFrame written to 'output_erased_dataset.csv'")