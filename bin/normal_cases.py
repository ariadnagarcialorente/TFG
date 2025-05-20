import numpy as np
import pandas as pd


#Test 1
df1 = pd.DataFrame(np.random.randn(100, 10), columns=[f'col{i}' for i in range(10)])
# Erase 60% of the values in col3 and col7
for col in ['col3', 'col7']:
    missing_indices = np.random.choice(df1.index, size=60, replace=False)
    df1.loc[missing_indices, col] = np.nan


#Test 2
df2 = pd.DataFrame(np.random.randn(100, 10), columns=[f'col{i}' for i in range(10)])
# Select 10 rows that will have a lot of missing values
rows_with_missing = np.random.choice(df2.index, size=10, replace=False)
for row in rows_with_missing:
    missing_cols = np.random.choice(df2.columns, size=6, replace=False)
    df2.loc[row, missing_cols] = np.nan

#Test 3
df3 = pd.DataFrame(np.random.randn(100, 10), columns=[f'col{i}' for i in range(10)])
# Create a block of 20x3 of missing values (rows 30-50, columns 2-4)
df3.loc[30:50, ['col2', 'col3', 'col4']] = np.nan

#Test 4
df4 = pd.DataFrame({
    'age': np.random.randint(18, 80, 100),
    'education': np.random.choice(['High School', 'Bachelors', 'Masters', 'PhD'], 100),
    'income': np.random.normal(30000, 10000, 100),
    'health_score': np.random.normal(50, 10, 100)
})

# We simulate that people olfer than 60 have no "education"
df4.loc[df4['age'] > 60, 'education'] = np.nan

#Test 5

df5 = pd.DataFrame(np.random.randn(100, 10), columns=[f'col{i}' for i in range(10)])
# 10% of the values are missing ranomly
for _ in range(int(df5.size * 0.10)):
    i = np.random.randint(0, df5.shape[0])
    j = np.random.randint(0, df5.shape[1])
    df5.iat[i, j] = np.nan

df2.to_csv('output_erased_dataset.csv', index=False)

