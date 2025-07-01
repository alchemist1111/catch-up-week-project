import mysql.connector
from mysql.connector import Error
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database connection function
def create_database_connection():
    try:
        eventdb = mysql.connector.connect(
            host = os.getenv('DB_HOST'),
            user = os.getenv('DB_USER'),
            password = os.getenv('DB_PASSWORD'),
            database = os.getenv('DB_NAME')
        )
        
        # Check if the connection was successful
        if eventdb.is_connected():
            return eventdb
        else:
            raise Error("Failed to connect to the database")
    
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None
    
    finally:
        if eventdb and eventdb.is_connected():
            eventdb.close()


# User class
class User:
    # Constructor to initialize user attributes
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.created_at = datetime.now()
        
    # Function to save user to the database
    def register(self):
        dbconn = create_database_connection()
        if dbconn is None:
            print("Database connection failed. User registration aborted.")
            return
        cursor = None
        try:
            cursor = dbconn.cursor()
            cursor.execute("INSERT INTO users (first_name, last_name, email, password, created_at) VALUES (%s, %s, %s, %s, %s)", 
                           (self.first_name, self.last_name, self.email, self.password, self.created_at))
            dbconn.commit() # Commit the transaction
            print("User registered successfully.")
        except Error as e:
            print(f"Error while inserting user data: {e}")
            dbconn.rollback()  # Rollback in case of error
            
        finally:
            if dbconn.is_connected():
                cursor.close()
                dbconn.close()        
      