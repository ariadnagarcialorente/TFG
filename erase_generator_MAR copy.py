import pandas as pd
import numpy as np
import random


def delete_MAR_1_to_x(data, x_vars, p_miss=0.2, seed=None):
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Make a copy of the data
    data_mar = data.copy()
    
    # Create a probability of missingness based on x_vars
    # We use the rank of the sum of x_vars to determine probability
    if len(x_vars) > 0:
        # Normalize values between 0 and 1 for each x_var
        probs = np.zeros(len(data))
        for var in x_vars:
            if var in data.columns:
                # Add normalized values of each variable
                var_values = data[var].values
                if not all(pd.isna(var_values)):
                    normalized = (var_values - np.nanmin(var_values)) / (np.nanmax(var_values) - np.nanmin(var_values))
                    probs += normalized
        
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
    
    # Identify the target variable (the first column that's not in x_vars)
    target_var = [col for col in data.columns if col not in x_vars][0] if x_vars else data.columns[0]
    
    # Set values to missing
    data_mar.loc[missing_mask, target_var] = np.nan
    
    return data_mar



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