import pandas as pd
import random


Percent=float(input("Insert a number between 0 and 100: "))

data = pd.read_csv('output_complete_dataset.csv')

total_cells = data.size

n_cells_to_swap = int(total_cells * (Percent / 100))

all_indices = [(i, j) for i in range(data.shape[0]) for j in range(data.shape[1])]

indices_to_swap = random.sample(all_indices, n_cells_to_swap)

for row_idx, col_idx in indices_to_swap:
        data.iloc[row_idx, col_idx] = None

df = pd.DataFrame(data)

print(df.head())


df.to_csv('output_erased_dataset.csv', index=False)

print("Complete DataFrame written to 'output_erased_dataset.csv'")