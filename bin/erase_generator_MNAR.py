import pandas as pd
import numpy as np
import random




def delete_MNAR_1_to_x(data, target_var, x_vars=None, p_miss=0.2, seed=None):
    """
    Create MNAR values using MNAR1:x mechanism.
    
    In this method, the probability of a value being missing depends on
    the value itself and potentially other variables.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The dataframe containing the data.
    target_var : str
        The column name where missing values will be introduced.
    x_vars : list, optional
        List of additional column names that will influence missingness.
    p_miss : float, default=0.2
        The overall proportion of missing values to generate.
    seed : int, optional
        Random seed for reproducibility.
        
    Returns:
    --------
    pandas.DataFrame
        A copy of the original dataframe with MNAR values.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mnar = data.copy()
    
    # Initialize probabilities based on target variable
    if pd.api.types.is_numeric_dtype(data[target_var]):
        # For numeric target variables
        target_values = data[target_var].values
        
        # Normalize target values to [0, 1] range
        if np.nanmax(target_values) > np.nanmin(target_values):
            probs = (target_values - np.nanmin(target_values)) / (np.nanmax(target_values) - np.nanmin(target_values))
        else:
            probs = np.ones(len(data)) * 0.5
    else:
        # For categorical target variables, use frequency-based approach
        value_counts = data[target_var].value_counts(normalize=True)
        
        # Less frequent categories have higher probability of being missing
        probs = np.array([1 - value_counts.get(val, 0) for val in data[target_var]])
        
        # Normalize probabilities
        if np.max(probs) > np.min(probs):
            probs = (probs - np.min(probs)) / (np.max(probs) - np.min(probs))
        else:
            probs = np.ones(len(data)) * 0.5
    
    # Add influence from additional variables if specified
    if x_vars is not None and len(x_vars) > 0:
        for var in x_vars:
            if var in data.columns and var != target_var:
                if pd.api.types.is_numeric_dtype(data[var]):
                    # For numeric variables
                    var_values = data[var].values
                    if np.nanmax(var_values) > np.nanmin(var_values):
                        # Normalize and add to probabilities
                        var_norm = (var_values - np.nanmin(var_values)) / (np.nanmax(var_values) - np.nanmin(var_values))
                        probs += var_norm
                else:
                    # For categorical variables
                    value_counts = data[var].value_counts(normalize=True)
                    cat_probs = np.array([1 - value_counts.get(val, 0) for val in data[var]])
                    
                    # Normalize categorical probabilities
                    if np.max(cat_probs) > np.min(cat_probs):
                        cat_probs = (cat_probs - np.min(cat_probs)) / (np.max(cat_probs) - np.min(cat_probs))
                        probs += cat_probs
        
        # Re-normalize to [0, 1]
        if np.max(probs) > np.min(probs):
            probs = (probs - np.min(probs)) / (np.max(probs) - np.min(probs))
    
    # Adjust probabilities to achieve desired missingness rate
    probs = probs * p_miss * 2  # Scale to have average close to p_miss
    
    # Cap probabilities at 1
    probs = np.minimum(probs, 1)
    
    # Determine which values will be missing
    missing_mask = np.random.random(len(data)) < probs
    
    # Set values to missing
    data_mnar.loc[missing_mask, target_var] = np.nan
    
    return data_mnar


def delete_MNAR_censoring(data, target_var, p_miss=0.2, censoring_tail="right", seed=None):
    """
    Create MNAR values using a censoring mechanism.
    
    In this method, values in target_var are more likely to be missing when 
    they are in the specified tail of its distribution.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        The dataframe containing the data.
    target_var : str
        The column name where missing values will be introduced.
    p_miss : float, default=0.2
        The overall proportion of missing values to generate.
    censoring_tail : str, default="right"
        Which tail of the distribution to censor. Can be "right" or "left".
    seed : int, optional
        Random seed for reproducibility.
        
    Returns:
    --------
    pandas.DataFrame
        A copy of the original dataframe with MNAR values.
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mnar = data.copy()
    
    if pd.api.types.is_numeric_dtype(data[target_var]):
        # For numeric variables, use ranking approach
        target_values = data[target_var].values
        
        # Create probability of missing based on the target variable itself
        if censoring_tail == "right":
            # Higher values have higher probability of missing
            probs = stats.rankdata(target_values) / len(target_values)
        else:  # "left"
            # Lower values have higher probability of missing
            probs = 1 - (stats.rankdata(target_values) / len(target_values))
    else:
        # For categorical variables, use frequency-based approach
        value_counts = data[target_var].value_counts(normalize=True)
        
        if censoring_tail == "right":
            # Less frequent categories have higher probability of being missing
            probs = np.array([1 - value_counts.get(val, 0) for val in data[target_var]])
        else:  # "left"
            # More frequent categories have higher probability of being missing
            probs = np.array([value_counts.get(val, 0) for val in data[target_var]])
        
        # Normalize probabilities
        if np.max(probs) > np.min(probs):
            probs = (probs - np.min(probs)) / (np.max(probs) - np.min(probs))
        else:
            probs = np.ones(len(data)) * 0.5
    
    # Adjust probabilities to achieve desired missingness rate
    probs = probs * p_miss * 2  # Scale to have average close to p_miss
    
    # Cap probabilities at 1
    probs = np.minimum(probs, 1)
    
    # Determine which values will be missing
    missing_mask = np.random.random(len(data)) < probs
    
    # Set values to missing
    data_mnar.loc[missing_mask, target_var] = np.nan
    
    return data_mnar


=0.2, group_val=None, seed=None):

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mnar = data.copy()
    
    # Determine group value if not specified
    if group_val is None:
        # Use the group with higher average target values
        group_means = data.groupby(group_var)[target_var].mean()
        group_val = group_means.idxmax()
    
    # Create mask for the specified group
    group_mask = data[group_var] == group_val
    
    # Determine target values for the selected group
    target_values_in_group = data.loc[group_mask, target_var].values
    
    # Sort indices by target values (largest values have highest probability)
    sorted_indices = np.argsort(-target_values_in_group)
    
    # Calculate how many values to delete
    n_missing = int(p_miss * sum(group_mask))
    
    if n_missing > 0:
        # Get indices of values to set to missing
        indices_to_miss = np.where(group_mask)[0][sorted_indices[:n_missing]]
        
        # Set values to missing
        data_mnar.loc[indices_to_miss, target_var] = np.nan
    
    return data_mnar


def delete_MNAR_rank(data, target_var, p_miss=0.2, seed=None):

    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mnar = data.copy()
    
    # Get the ranks of the target variable
    ranks = stats.rankdata(data[target_var].values)
    
    # Calculate probability of missingness based on rank
    probs = ranks / len(data)
    
    # Adjust probabilities to achieve desired missingness rate
    probs = probs * p_miss * 2  # Scale to have average close to p_miss
    
    # Cap probabilities at 1
    probs = np.minimum(probs, 1)
    
    # Determine which values will be missing
    missing_mask = np.random.random(len(data)) < probs
    
    # Set values to missing
    data_mnar.loc[missing_mask, target_var] = np.nan
    
    return data_mnar

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