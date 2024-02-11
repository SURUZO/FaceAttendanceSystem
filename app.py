import mysql.connector
import pandas as pd
import base64

# Connect to the FaceRecognition database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root@123",
    database="FaceRecognition"
)

# Create a cursor object to interact with the database
cursor = mydb.cursor()

# Fetch all data from the Record table
cursor.execute("SELECT * FROM Record")
data = cursor.fetchall()

# Close the database connection
cursor.close()
mydb.close()

# Convert the data to a pandas DataFrame
columns = ['ID', 'Name', 'Major', 'Starting Year', 'Total Attendance', 'Standing', 'Year', 'Last Attendance Time', 'Image']
df = pd.DataFrame(data, columns=columns)

# Convert binary image data to base64 format and add CSS styling
def convert_image_to_html(image_data):
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    return f'<img src="data:image/jpeg;base64,{image_base64}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 5px;">'

df['Image'] = df['Image'].apply(convert_image_to_html)

# Convert the DataFrame to an HTML table
html_table = df.to_html(index=False, escape=False)

# Adding CSS style to the HTML table
html_table_with_style = f"""
<html>
<head>
<style>
table {{
    border-collapse: collapse;
    width: 100%;
}}

th, td {{
    padding: 8px;
    text-align: left;
    border-bottom: 1px solid #ddd;
}}

img {{
    width: 100px;
    height: 100px;
    object-fit: cover;
    border-radius: 5px;
}}
</style>
</head>
<body>
{html_table}
</body>
</html>
"""

# Save the HTML table to a file
with open('output_table.html', 'w') as file:
    file.write(html_table_with_style)

print("Database output successfully to 'output_table.html'.")
