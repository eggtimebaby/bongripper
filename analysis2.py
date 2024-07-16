import os
import json
import pandas as pd

# Directory containing the JSON files
directory = 'smoke_data'

# Initialize an empty list to hold the data
data_list = []

# Loop through all files in the directory
for filename in os.listdir(directory):
    if filename.endswith('.json'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r') as file:
            data = json.load(file)
            # Assuming 'log_data' key holds the list of records
            data_list.extend(data['log_data'])

# Create a DataFrame from the combined data
df = pd.DataFrame(data_list)

# Save the DataFrame to a CSV file
df.to_csv('combined_sensor_data.csv', index=False)
