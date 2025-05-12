import pandas as pd
from faker import Faker
import random

# Initialize the Faker object
fake = Faker()

# Get user input for the number of columns and rows
columns = int(input("Indicate a number between 1 and 30 for the columns: "))
rows = int(input("Indicate a number between 100 and 999 for the rows: "))

# Dictionary mapping Faker methods to column names
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
    "date_of_birth": "Date_of_Birth",
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
    "currency_code": "Currency",  # Changed from "currency" to "currency_code" which is a valid Faker method
    "credit_card_number": "Credit_Card_Number",
    "boolean": "Boolean",
    "uuid4": "uuid4",
    "hex_color": "Hex_Colour",
    "license_plate": "License_Plate",
    "vin": "Vin",
    "isbn10": "ISBN",
    "catch_phrase": "Catch_Phrase"
}

# Initialize an empty dictionary to store our data
data = {}

# Get only the number of columns we need from our faker dictionary
selected_faker_methods = list(faker_dictionary.items())[:columns]

# Dictionary to store the limited instances of each faker category
generated_data = {}

# Generate a limited set of faker instances for each column (between 1 and 15)
for func, column_name in selected_faker_methods:
    try:
        faker_method = getattr(fake, func)
        # Generate between 1 and 15 unique values for this category
        num_instances = random.randint(1, 15)
        unique_values = []
        
        # Generate the unique instances
        for _ in range(num_instances):
            unique_values.append(faker_method())
            
        generated_data[column_name] = unique_values
    except AttributeError:
        print(f"Warning: Faker method '{func}' not found. Using placeholder.")
        generated_data[column_name] = [f"placeholder_{func}"]

# For each column, generate data by randomly selecting from the limited instances
for column_name, instances in generated_data.items():
    # Create a list of fake data for this column
    column_data = []
    
    # Generate the specified number of rows by randomly selecting from the instances
    for _ in range(rows):
        random_instance = random.choice(instances)
        column_data.append(random_instance)
    
    # Add the column to our data dictionary
    data[column_name] = column_data

# Create the DataFrame
df = pd.DataFrame(data)

# Display the first few rows of the DataFrame
print("\nPreview of the generated data:")
print(df.head())

# Save the DataFrame to a CSV file named 'output_complete_dataset.csv'
df.to_csv('output_complete_dataset.csv', index=False)

# Print a confirmation message to let the user know the file was created successfully
print("\nComplete DataFrame written to 'output_complete_dataset.csv'")