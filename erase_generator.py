import pandas as pd
import random


Percent=float(input("Insert a percentage between 0 and 100 to be erased: "))

data = pd.read_csv('output_complete_dataset.csv')

number_data = data.size

to_erase = int(number_data * (Percent / 100))

indices = [(i, j) for i in range(data.shape[0]) for j in range(data.shape[1])]

to_delete = random.sample(indices, to_erase)

for row, col in to_delete:
        data.iloc[row, col] = None

df = pd.DataFrame(data)

print(df.head())


df.to_csv('output_erased_dataset.csv', index=False)

print("Complete DataFrame written to 'output_erased_dataset.csv'")