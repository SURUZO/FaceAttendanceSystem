import mysql.connector
import os
from tkinter import *
from PIL import Image, ImageTk

# Connect to MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root@123"
)

# Create a cursor object to interact with the database
cursor = mydb.cursor()

# Check if the database already exists
cursor.execute("SHOW DATABASES")
databases = cursor.fetchall()
database_exists = False
database_name="FaceRecognition"

for database in databases:
    if database_name in database:
        database_exists = True
        break

# Create the database if it doesn't exist
if not database_exists:
    cursor.execute("CREATE DATABASE FaceRecognition")
    print("Database 'FaceRecognition' created.")
else:
    print("Database 'FaceRecognition' already exists.")

# Connect to the FaceRecognition database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root@123",
    database="FaceRecognition"
)

# Create a cursor object to interact with the database
cursor = mydb.cursor()

# Create the Record table if it doesn't exist
cursor.execute("CREATE TABLE IF NOT EXISTS Record ("
               "id VARCHAR(20) PRIMARY KEY, "
               "name VARCHAR(100), "
               "major VARCHAR(100), "
               "starting_year INT(4), "
               "total_attendance INT, "
               "standing CHAR(1), "
               "year INT, "
               "last_attendance_time DATETIME, "
               "image LONGBLOB"
               ")")

# Accessing Images folder
folderPath = 'Images'
imageList = os.listdir(folderPath)

def process_images():
    for imageFile in imageList:
        imagePath = os.path.join(folderPath, imageFile)
        id = os.path.splitext(imageFile)[0]

        # Check if the image ID already exists in the database
        cursor.execute("SELECT id FROM Record WHERE id = %s", (id,))
        existing_id = cursor.fetchone()

        if existing_id:
            print(f"Image with ID {id} already exists in the database. Skipping...")
            continue

        # Create Tkinter GUI
        root = Tk()
        root.title("Face Recognition")
        root.geometry("400x450")

        # Create image label
        image_label = Label(root)
        image_label.pack()

        # Create input fields
        id_label = Label(root, text="ID:")
        id_label.pack()
        id_entry = Entry(root)
        id_entry.pack()

        name_label = Label(root, text="Name:")
        name_label.pack()
        name_entry = Entry(root)
        name_entry.pack()

        major_label = Label(root, text="Major:")
        major_label.pack()
        major_entry = Entry(root)
        major_entry.pack()

        starting_year_label = Label(root, text="Starting Year:")
        starting_year_label.pack()
        starting_year_entry = Entry(root)
        starting_year_entry.pack()

        total_attendance_label = Label(root, text="Total Attendance:")
        total_attendance_label.pack()
        total_attendance_entry = Entry(root)
        total_attendance_entry.pack()

        standing_label = Label(root, text="Standing:")
        standing_label.pack()
        standing_entry = Entry(root)
        standing_entry.pack()

        year_label = Label(root, text="Year:")
        year_label.pack()
        year_entry = Entry(root)
        year_entry.pack()

        last_attendance_time_label = Label(root, text="Last Attendance Time:")
        last_attendance_time_label.pack()
        last_attendance_time_entry = Entry(root)
        last_attendance_time_entry.pack()

        def save_image_data():
            # Read the image file
            with open(imagePath, 'rb') as file:
                imageBinary = file.read()

            # Get input values from the user
            id = id_entry.get()
            name = name_entry.get()
            major = major_entry.get()
            starting_year = starting_year_entry.get()
            total_attendance = total_attendance_entry.get()
            standing = standing_entry.get()
            year = year_entry.get()
            last_attendance_time = last_attendance_time_entry.get()

            # Insert data into the Record table
            insert_query = "INSERT INTO Record (id, name, major, starting_year, total_attendance, standing, year, last_attendance_time, image) " \
                           "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data = (id, name, major, starting_year, total_attendance, standing, year, last_attendance_time, imageBinary)
            cursor.execute(insert_query, data)
            mydb.commit()

            print(f"Image with ID {id} inserted into the database.")

            # Close the Tkinter window after saving data
            root.destroy()

        # Display image in the GUI
        image = Image.open(imagePath)
        image = image.resize((200, 200), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        image_label.config(image=photo)
        image_label.image = photo

        # Pre-fill the ID field
        id_entry.delete(0, END)
        id_entry.insert(0, id)

        # Create save button
        save_button = Button(root, text="Save", command=save_image_data)
        save_button.pack()

        # Run the Tkinter event loop
        root.mainloop()

    # Close the database connection
    cursor.close()
    mydb.close()

# Start processing the images
process_images()
