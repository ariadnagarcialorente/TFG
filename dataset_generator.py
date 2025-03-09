import pandas as pd
from faker import Faker

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
    "date_of_birth": "Date_of_birth",
    "company": "Company",
    "job": "Job",
    "latitude":"Latitude",
    "longitude":"Longitude",
    "date_time":"Date_Time",
    "date_this_century":"Date_this_century",
    "date_this_decade":"Date_this_decade",
    "time":"Time",
    "word":"Word",
    "company_suffix":"Company_Suffix",
    "currency":"Currency",
    "credit_card_number":"Credit_Card_Number",
    "boolean":"Boolean",
    "uuid4":"uuid4",
    "hex_color":"Hex_Colour",
    "license_plate": "License_Plate",
    "vin":"Vin",
    "isbn10":"ISBN",
    "catch_phrase":"Catch_Phrase"
}

# Initialize an empty dictionary to store our data

data = {}

# Get only the number of columns we need from our faker dictionary
selected_faker_methods = list(faker_dictionary.items())[:columns]

# For each method and column name in our selected methods
for method, name in selected_faker_methods:
    # Create a list of fake data for this column
    column_data = []
    
    # Generate the specified number of rows
    for i in range(rows):
        # Get the appropriate Faker method
        faker_method = getattr(fake, method)
        # Call the method to generate fake data and add to our column
        fake_value = faker_method()
        column_data.append(fake_value)
    
    # Add the column to our data dictionary
    data[name] = column_data

# Create the DataFrame
df = pd.DataFrame(data)

# Display the first few rows of the DataFrame
print(df.head())

# Save the DataFrame to a CSV file named 'output_complete_dataset.csv'
df.to_csv('output_complete_dataset.csv', index=False)

# Print a confirmation message to let the user know the file was created successfully
print("Complete DataFrame written to 'output_complete_dataset.csv'")