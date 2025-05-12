import pandas as pd
import numpy as np

# Get user input for the number of columns and rows
columns = int(input("Indicate a number between 1 and 30 for the columns: "))
rows = int(input("Indicate a number between 100 and 999 for the rows: "))

# Validate inputs
if not (1 <= columns <= 30 and 1 <= rows <= 999):
    raise ValueError("Invalid input. Columns must be between 1-30 and rows between 100-999.")

# Generate random numerical data
data = np.random.randn(0, 101, size=(rows, columns))  # Random integers from 0 to 100

# Create the DataFrame
df = pd.DataFrame(data, columns=[f'col_{i+1}' for i in range(columns)])

# Display the first few rows of the DataFrame
print(df.head())

# Save the DataFrame to a CSV file named 'output_complete_dataset.csv'
df.to_csv('output_complete_dataset.csv', index=False)

# Print a confirmation message to let the user know the file was created successfully
print("Complete DataFrame written to 'output_complete_dataset.csv'")
