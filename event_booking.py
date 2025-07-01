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
            # Close the cursor and connection
            if cursor and dbconn.is_connected():
                cursor.close()
                dbconn.close()
                
    # Static method for user login
    @staticmethod
    def login(email, password):
        dbconn = create_database_connection()
        if dbconn is None:
            print("Database connection failed. User registration aborted.")
            return False
        cursor = None
        try:
            cursor = dbconn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone() # Fetch the first matching user
            
            if user:
                print(f'{user[1]} {user[2]} logged in successfully.')
                return True # User found, login successful
            else:
                print("Invalid email or password.")
                return False # User not found, login failed
        except Error as e:
            print(f"Error while fetching user data: {e}")
            return False # Error occurred during login
        finally:
            # Close the cursor and connection
            if cursor and dbconn.is_connected():
                cursor.close()
                dbconn.close()
                
# Event class
class Event:
    # Constructor to initialize event attributes
    def __init__(self, name, description, event_date, event_time, location, available_seats, created_at=None):
        self.name = name
        self.description = description
        self.event_date = event_date
        self.event_time = event_time
        self.location = location
        self.available_seats = available_seats
        self.created_at = created_at or datetime.now() 
        
    # Static method to view all events
    @staticmethod
    def view_all_events():
        dbconn = create_database_connection()
        
        if dbconn is None:
            print("Database connection failed. Unable to fetch events.")
            return []
        cursor = dbconn.cursor()
        try:
            cursor.execute("SELECT * FROM events") # Fetch all events
            events = cursor.fetchall() # Get all events
            return events # Return the list of events
        except Error as e:
            print(f"Error while fetching events: {e}")
            return []
        finally:
            # Close the cursor and connection
            if cursor and dbconn.is_connected():
                cursor.close()
                dbconn.close()
    
    # Static method to view a specific event by ID
    @staticmethod
    def view_event_by_id(event_id):
        dbconn = create_database_connection()
        
        if dbconn is None:
            print("Database connection failed. Unable to fetch event.")
            return None
        
        cursor = dbconn.cursor() # Create cursor for executing queries
        
        try:
            # SQL query to fetch event by id
            cursor.execute("SELECT * FROM events WHERE id = %s", (event_id,))
            event = cursor.fetchone() # Fetch the event
            
            if event:
                return event
            else:
                print(f"No event found with ID {event_id}.")
                return None
        except Error as e:
            print(f"Error while fetching event: {e}")
            return None
        finally:
            # Close the cursor and database connection
            if cursor and dbconn.is_connected():
                cursor.close()
                dbconn.close()    
                

# Booking class
class Booking:
    # Constructor to initialize booking attributes
    def __init__(self, user_id, event_id, tickets_booked):
        self.user_id = user_id
        self.event_id = event_id
        self.tickets_booked = tickets_booked
        self.booking_date = datetime.now()

    # Function to make a booking
    def make_booking(self):
        event = Event.view_event_by_id(self.event_id)

        if event is None:
            print("Event not found. Booking cannot be made.")
            return False

        # Assuming the event data has 'available_seats' at index 5
        available_seats = event[5]  # Adjust the index based on your table structure

        if self.tickets_booked > available_seats:
            print("Not enough available seats. Booking cannot be made.")
            return False

        # Proceed with booking if enough seats are available
        dbconn = create_database_connection()

        if dbconn is None:
            print("Database connection failed. Booking cannot be made.")
            return False

        cursor = dbconn.cursor()
        try:
            # Insert booking into the database
            cursor.execute(
                "INSERT INTO bookings (user_id, event_id, tickets_booked, booking_date) VALUES (%s, %s, %s, %s)",
                (self.user_id, self.event_id, self.tickets_booked, self.booking_date)
            )

            dbconn.commit()  # Commit the transaction
            print("Booking made successfully.")

            # Update the available seats for the event
            new_available_seats = available_seats - self.tickets_booked
            cursor.execute(
                "UPDATE events SET available_seats = %s WHERE id = %s", 
                (new_available_seats, self.event_id)
            )
            dbconn.commit()  # Commit the seat update

            return True
        except Error as e:
            print(f"Error during booking: {e}")
            return False
        finally:
            if cursor and dbconn.is_connected():
                cursor.close()
                dbconn.close()  # Close the connection after use 
          