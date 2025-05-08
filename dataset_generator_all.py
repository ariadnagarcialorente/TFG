import pandas as pd
import numpy as np
from faker import Faker
import random

# Initialize the Faker object
fake = Faker()

# Get user input for the number of columns and rows
columns = int(input("Indicate a number between 1 and 30 for the columns: "))
rows = int(input("Indicate a number between 100 and 999 for the rows: "))

# Validate input ranges
if not (1 <= columns <= 30 and 100 <= rows <= 999):
    raise ValueError("Invalid input. Columns must be between 1-30 and rows between 100-999.")

# Faker methods dictionary
faker_dictionary = {
    "first_name": "First_Name",
    "last_name": "Last_Name",
    "user_name": "User_Name",
    "ascii_free_email": "Email",
    "phone_number": "Phone_Number",
    "address": "Address",
    "country": "Country",
    "city": "City",
    "state": "State",
    "zipcode": "Zipcode",
    "date_of_birth": "Date_of_birth",
    "company": "Company",
    "job": "Job",
    "latitude": "Latitude",
    "longitude": "Longitude",
    "date_time": "Date_Time",
    "date_this_century": "Date_this_century",
    "date_this_decade": "Date_this_decade",
    "time": "Time",
    "word": "Word",
    "company_suffix": "Company_Suffix",
    "currency": "Currency",
    "credit_card_number": "Credit_Card_Number",
    "boolean": "Boolean",
    "uuid4": "UUID",
    "hex_color": "Hex_Colour",
    "license_plate": "License_Plate",
    "vin": "VIN",
    "isbn10": "ISBN",
    "catch_phrase": "Catch_Phrase"
}

faker_methods = list(faker_dictionary.items())
random.shuffle(faker_methods)

# Decide randomly how many numerical vs. categorical columns to generate
num_faker_cols = random.randint(1, min(columns, len(faker_methods)))
num_numeric_cols = columns - num_faker_cols

data = {}

# Generate faker-based categorical columns
for method, name in faker_methods[:num_faker_cols]:
    faker_func = getattr(fake, method)
    data[name] = [faker_func() for _ in range(rows)]

# Generate numerical columns with random data
for i in range(num_numeric_cols):
    col_name = f"num_col_{i+1}"
    data[col_name] = np.random.randint(0, 101, size=rows)  # Random integers 0–100

# Create the DataFrame
df = pd.DataFrame(data)

# Display the first few rows of the DataFrame
print(df.head())

# Save to CSV
df.to_csv('output_complete_dataset.csv', index=False)
print("Complete DataFrame written to 'output_complete_dataset.csv'")
