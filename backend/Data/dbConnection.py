
# This file is responsible for creating a connection to the database

import mysql.connector


# Returns database object
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='host.docker.internal',   
            port=3307,         
            user='root',        
            password='rootpassword', 
            database='dbname'
        )
        if connection.is_connected():
            print("Tset s")
            return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


print("get Database connection " + str(get_db_connection()))