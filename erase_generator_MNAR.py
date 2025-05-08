import pandas as pd
import numpy as np
import random


#delete_MAR_1_to_x()
# ds_comp -> complete dataset
# p -> missingness proportion is 0 <= p < 1
# [miss_col] -> target variable for missingness 
# [dep_col] -> depending variables for missingness
# x -> how many variables
# cutoff_fun -> Funtion to compute cutoff
# random_seed -> rand seed
def delete_MAR_1_to_x(df, cols_mis, cols_ctrl, p, x, cutoff_fun=np.median, warn=True):
    df = df.copy()
    # Validate inputs
    if len(cols_mis) != len(cols_ctrl):
        raise ValueError("cols_mis and cols_ctrl must have the same length")
    
    if isinstance(p, (int, float)):
        p = [p] * len(cols_mis)
    elif len(p) != len(cols_mis):
        raise ValueError("p must be scalar or have same length as cols_mis")
    
    for i in range(len(cols_mis)):
        mis_col = cols_mis[i]
        ctrl_col = cols_ctrl[i]
        p_i = p[i]
        nrow = len(df)
        total_na = round(nrow * p_i)
        
        if total_na == 0:
            continue
        
        # Calculate cutoff
        ctrl_values = df[ctrl_col]
        cutoff = cutoff_fun(ctrl_values)
        
        # Determine groups
        group1_mask = ctrl_values < cutoff
        if group1_mask.sum() == 0:
            group1_mask = ctrl_values <= cutoff
        
        group1_indices = df.index[group1_mask]
        group2_indices = df.index[~group1_mask]
        n1 = len(group1_indices)
        n2 = len(group2_indices)
        
        # Handle edge cases with empty groups
        if n1 == 0 or n2 == 0:
            k1 = min(total_na, n1) if n2 == 0 else 0
            k2 = min(total_na, n2) if n1 == 0 else 0
        else:
            # Check if p and x are feasible
            max_feasible_na = (n1 / x) + n2
            x_used = x
            
            if total_na > max_feasible_na:
                x_adj = n1 / (total_na - n2) if (total_na - n2) > 0 else np.inf
                x_used = x_adj
            
            # Calculate ideal missing distribution
            denominator = n1 + x_used * n2
            if denominator == 0:
                k1, k2 = 0, min(total_na, n2)
            else:
                k1_ideal = (total_na * n1) / denominator
                k1 = int(np.round(k1_ideal))
                
                # Clamp values to valid ranges
                k1 = max(0, min(n1, k1))
                k2 = total_na - k1
                k2 = max(0, min(n2, k2))
                k1 = max(0, min(n1, total_na - k2))
        
        # Select indices to make missing
        na_indices = []
        if k1 > 0:
            na_indices += np.random.choice(group1_indices, k1, replace=False).tolist()
        if k2 > 0:
            na_indices += np.random.choice(group2_indices, k2, replace=False).tolist()
        
        # Apply missing values
        df.loc[na_indices, mis_col] = np.nan
    
    return df


# Get user input for percentage of data to erase
Percent = float(input("Insert a percentage between 0 and 100 to be erased: "))

# Load dataset from CSV file
data = pd.read_csv('output_complete_dataset.csv')

# Calculate total number of data points
number_data = data.size

# Calculate how many data points to erase
num_erase = int(number_data * (Percent / 100))

erased_act = 0

while num_erase > erased_act:
    # Select Y and X randomly (X != Y)
    Y = np.random.choice(data.columns)
    X = np.random.choice(data.columns.drop(Y))

    prob = random.rand()

    print(prob)

    if prob > 0.75:
        X = ""
        erased_act += 1

    
    
# Convert to DataFrame (note: this step is redundant as data is already a DataFrame)
df = pd.DataFrame(data)

# Display first 5 rows of modified data
print(df.head())

# Save modified dataset to new CSV file
df.to_csv('output_erased_dataset.csv', index=False)

# Confirm completion
print("Complete DataFrame written to 'output_erased_dataset.csv'")