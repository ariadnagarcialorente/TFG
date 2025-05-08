# Import required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sn

# Load the dataset with missing values
data = pd.read_csv('output_erased_dataset.csv')


# Get user input for the algorithm
rows = int(input("Indicate the minimum number of rows: "))
rel_rows = int(input("Indicate the minimum percent of rows: "))

og_rows = data.shape[0]

#print(og_rows)

data['na_count'] = data.isna().sum(axis=1) 
data = data.sort_values(by='na_count', ascending=False) 

while data.shape[0] > rows and 100*data.shape[0]/og_rows > rel_rows:
    data = data.iloc[1:]

# Drop the 'na_count' column (as it's no longer needed)
data = data.drop(columns=['na_count'])

#print(data.shape[0])
if data.shape[0] == rows: 
    print('Minimum number of rows reached')
else: 
    print('Minimum percent of rows reached')

# Save the cleaned dataset
data.to_csv('cleaned_dataset.csv', index=False)
