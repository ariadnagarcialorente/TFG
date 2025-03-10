import pandas as pd
import random

# Get user input for percentage of data to erase
Percent = float(input("Insert a percentage between 0 and 100 to be erased: "))

# Load dataset from CSV file
data = pd.read_csv('output_complete_dataset.csv')

# Calculate total number of data points
number_data = data.size

# Calculate how many data points to erase
num_erase = int(number_data * (Percent / 100))

# Create list of all possible (row, column) coordinates in the dataframe
indices = [(i, j) for i in range(data.shape[0]) for j in range(data.shape[1])]

# Randomly select coordinates to erase
to_delete = random.sample(indices, num_erase)

# Replace selected values with None
for row, col in to_delete:
    data.iloc[row, col] = None

# Convert to DataFrame (note: this step is redundant as data is already a DataFrame)
df = pd.DataFrame(data)

# Display first 5 rows of modified data
print(df.head())

# Save modified dataset to new CSV file
df.to_csv('output_erased_dataset.csv', index=False)

# Confirm completion
print("Complete DataFrame written to 'output_erased_dataset.csv'")