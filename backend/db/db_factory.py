import mysql.connector
from mysql.connector import Error
from config import *  # Assuming config.py contains DATABASE_CONFIG and other necessary variables
# from services.gitscript import update_cloned_repo  # Assuming this is the right function
import os
import json


# LOCAL_REPO_PATH = '../anycast-census' 
# TEST_LOCAL_REPO_PATH = 'backend/anycast-census/2024/' 
# GITHUB_REPO_URL = "https://github.com/anycast-census/anycast-census.git"  

class Database:
    """Database class to manage the MySQL database connection."""

    def __init__(self):
        self.connection = None

    def update_cloned_repo(repo_path, repo_url):
        try:
            if not os.path.exists(repo_path):
                print(f"Cloning repository from {repo_url} to {repo_path}...")
                git.Repo.clone_from(repo_url, repo_path) 
                print(f"Repository cloned successfully at {repo_path}")
            else:
                print(f"Repository exists. Pulling the latest changes at {repo_path}...")
                repo = git.Repo(repo_path)
                repo.git.fetch()  
                repo.git.reset('--hard', 'origin/main') 
                print(f"Repository updated at {repo_path}")
        except Exception as e:
            print(f"Error updating repository: {e}")

    def connect(self):
        """Establishes a connection to the MySQL database."""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(**DATABASE_CONFIG)
                if self.connection.is_connected():
                    print("Database connection established.")
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            self.connection = None
        return self.connection
    
    def ensure_connection(self):
        """Ensures there is a valid database connection."""
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def close(self):
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def initialize_database(self):
        """Initializes the database by creating necessary tables."""
        self.ensure_connection()  
        cursor = self.connection.cursor()
        try:
            print("Starting database initialization...")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS LocationIPv4 (
                    Prefix TEXT,
                    Date TEXT,
                    Longitude TEXT,
                    Latitude TEXT,
                    City TEXT,
                    CodeCountry TEXT,
                    Id TEXT,
                    Count TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS LocationIPv6 (
                    Prefix TEXT,
                    Date TEXT,
                    Longitude TEXT,
                    Latitude TEXT,
                    City TEXT,
                    CodeCountry TEXT,
                    Id TEXT,
                    Count TEXT
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS IPv4 (
                    Prefix TEXT,
                    MAnycast_ICMPv4 TEXT,
                    MAnycast_TCPv4 TEXT,
                    MAnycast_UDPv4 TEXT,
                    iGreedyICMPv4 TEXT,
                    iGreedyTCPv4 TEXT,
                    MAnycast_ICMPv4_Count TEXT,
                    MAnycast_TCPv4_Count TEXT,
                    MAnycast_UDPv4_Count TEXT,
                    iGreedyICMPv4_Count TEXT,
                    iGreedyTCPv4_Count TEXT,
                    Date TEXT
                );
            """)
            cursor.execute("""
               CREATE TABLE IF NOT EXISTS IPv6 (
                Prefix VARCHAR(45),
                MAnycast_ICMPv6 TEXT,
                MAnycast_TCPv6 TEXT,
                MAnycast_UDPv6 TEXT,
                iGreedyICMPv6 TEXT,
                iGreedyTCPv6 TEXT,
                MAnycast_ICMPv6_Count TEXT,
                MAnycast_TCPv6_Count TEXT,
                MAnycast_UDPv6_Count TEXT,
                iGreedyICMPv6_Count TEXT,
                iGreedyTCPv6_Count TEXT,
                Date TEXT
            );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Stats (
                    Date TEXT,
                    ICMPv4_GCD_Nodes TEXT,
                    ICMPv6_GCD_Nodes TEXT,
                    Anycast_ICMPv4_Count TEXT,
                    Anycast_TCPv4_Count TEXT,
                    Anycast_UDPv4_Count TEXT,
                    GCD_ICMPv4_Count TEXT,
                    GCD_TCPv4_Count TEXT,
                    Anycast_ICMPv6_Count TEXT,
                    Anycast_TCPv6_Count TEXT,
                    Anycast_UDPv6_Count TEXT,
                    GCD_ICMPv6_Count TEXT,
                    GCD_TCPv6_Count TEXT
                );
            """)

            self.connection.commit()
            print("SQL tables created successfully.")
        except Error as e:
            print(f"Error executing query: {e}")
        finally:
            cursor.close()



    def update_daily_database(self):
        TEST_LOCAL_REPO_PATH = '../anycast-census/2024/03/21'
        """Updates the daily database with new data from JSON files."""
        # update_cloned_repo(LOCAL_REPO_PATH, GITHUB_REPO_URL)
        Directoryfiles = os.listdir(TEST_LOCAL_REPO_PATH)
        print("test " + str(Directoryfiles))
        for filename in Directoryfiles:
            print("File name " + filename)
            file_path = os.path.join(TEST_LOCAL_REPO_PATH, filename)
            
            if os.path.isfile(file_path) and filename.endswith(".json"):
                print(f"Processing file: {filename}")
                try:
                    with open(file_path, 'r') as file:
                        date = filename[:10]
                        stats = filename[:5]
                        version = filename[11:13]  
                        location = len(filename) > 18  
                        json_data = json.load(file)
                    if not location and version == "v6":
                        self.insert_v6(json_data, date)
                    if not location and version == "v4":
                        print("Empika ipv4?")
                        self.insert_v4(json_data, date)
                    if location and version == "v6":
                        self.insert_location_ipv6(json_data, date)
                    if location and version == "v4":
                        self.insert_location_ipv4(json_data, date)
                except json.JSONDecodeError as e:
                    print(f"Error reading JSON file {filename}: {e}")
                except Exception as e:
                    print(f"An error occurred with file {filename}: {e}")
            else:
                print(f"Skipping {filename}, it is not a file or not a JSON.")




    # Loops through
    # def update_daily_database(self):
    #     """Updates the daily database with new data from JSON files."""
        
    #     # Use os.walk to recursively go through all directories and files
    #     for dirpath, dirnames, filenames in os.walk(TEST_LOCAL_REPO_PATH):
    #         print(f"Scanning directory: {dirpath}")
            
    #         for filename in filenames:
    #             file_path = os.path.join(dirpath, filename)
                
    #             # Check if the current file is a JSON file
    #             if filename.endswith(".json"):
    #                 print(f"Processing file: {file_path}")
                    
    #                 try:
    #                     # Open and read the JSON file
    #                     with open(file_path, 'r') as file:
    #                         date = filename[:10]  # Extract date from filename
    #                         version = filename[11:13]  # Extract version from filename
    #                         location = len(filename) > 18  # Determine if there's a location based on filename length

    #                         json_data = json.load(file)
                        
    #                     # Call the appropriate insert function based on version and location
    #                     if not location and version == "v6":
    #                         self.insert_v6(json_data, date)
    #                     elif not location and version == "v4":
    #                         print("Processing IPv4 data")
    #                         self.insert_v4(json_data, date)
    #                     elif location and version == "v6":
    #                         self.insert_location_ipv6(json_data, date)
    #                     elif location and version == "v4":
    #                         self.insert_location_ipv4(json_data, date)
                    
    #                 except json.JSONDecodeError as e:
    #                     print(f"Error reading JSON file {filename}: {e}")
    #                 except Exception as e:
    #                     print(f"An error occurred with file {filename}: {e}")
    #             else:
    #                 print(f"Skipping {filename}, it is not a JSON file.")

   

    def insert_v4(self, json_data, date):
        """Inserts IPv4 data into the database."""
        sql_insert_query = """
            INSERT INTO IPv4(
                Prefix, 
                MAnycast_ICMPv4, 
                MAnycast_TCPv4, 
                MAnycast_UDPv4, 
                iGreedyICMPv4, 
                iGreedyTCPv4, 
                MAnycast_ICMPv4_Count, 
                MAnycast_TCPv4_Count, 
                MAnycast_UDPv4_Count, 
                iGreedyICMPv4_Count, 
                iGreedyTCPv4_Count, 
                Date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.connection.cursor()  
        try:
            for ipv4 in json_data:
                values = (
                    str(ipv4["prefix"]),
                    str(ipv4["characterization"]["MAnycastICMPv4"].get("anycast")),
                    str(ipv4["characterization"]["MAnycastTCPv4"].get("anycast")),
                    str(ipv4["characterization"]["MAnycastUDPv4"].get("anycast")),
                    str(ipv4["characterization"]["iGreedyICMPv4"].get("anycast")),
                    str(ipv4["characterization"]["iGreedyTCPv4"].get("anycast")),
                    str(ipv4["characterization"]["MAnycastICMPv4"].get("instances")),
                    str(ipv4["characterization"]["MAnycastTCPv4"].get("instances")),
                    str(ipv4["characterization"]["MAnycastUDPv4"].get("instances")),
                    str(ipv4["characterization"]["iGreedyICMPv4"].get("instances")),
                    str(ipv4["characterization"]["iGreedyTCPv4"].get("instances")),
                    date
                )
                cursor.execute(sql_insert_query, values)

          
            self.connection.commit()
            print(f"Inserted {len(json_data)} records into IPv4 table.")

        except Error as e:
            print(f"Error inserting into IPv4 table: {e}")
        finally:
            cursor.close()  


    
    def insert_v6(self, json_data, date):
        """Inserts IPv6 data into the database."""
        sql_insert_query = """
            INSERT INTO IPv6 (
                Prefix, 
                MAnycast_ICMPv6, 
                MAnycast_TCPv6, 
                MAnycast_UDPv6, 
                iGreedyICMPv6, 
                iGreedyTCPv6, 
                MAnycast_ICMPv6_Count, 
                MAnycast_TCPv6_Count, 
                MAnycast_UDPv6_Count, 
                iGreedyICMPv6_Count, 
                iGreedyTCPv6_Count, 
                Date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.connection.cursor()  
        try:
            print("mpika")
            for ipv6 in json_data:
             
                values = (
                str(ipv6["prefix"]), 
                str(ipv6["characterization"]["MAnycastICMPv6"].get("anycast")),
                str(ipv6["characterization"]["MAnycastTCPv6"].get("anycast")),
                str(ipv6["characterization"]["MAnycastUDPv6"].get("anycast")),
                str(ipv6["characterization"]["iGreedyICMPv6"].get("anycast")),
                str(ipv6["characterization"]["iGreedyTCPv6"].get("anycast")),
                str(ipv6["characterization"]["MAnycastICMPv6"].get("instances")),
                str(ipv6["characterization"]["MAnycastTCPv6"].get("instances")),
                str(ipv6["characterization"]["MAnycastUDPv6"].get("instances")),
                str(ipv6["characterization"]["iGreedyICMPv6"].get("instances")),
                str(ipv6["characterization"]["iGreedyTCPv6"].get("instances")),
                str(date)  
                )
                cursor.execute(sql_insert_query, values)

            
            self.connection.commit()
            print(f"Inserted {len(json_data)} records into IPv6 table.")

        except Error as e:
            print(f"Error inserting into IPv6 table: {e}")
        finally:
            cursor.close()  

    def insert_location_ipv6(self, json_data, date):
        """Inserts location data for IPv6 into the database."""
        
        sql_insert_query = """
            INSERT INTO LocationIPv6 (
                Prefix, 
                Date, 
                Longitude, 
                Latitude, 
                City, 
                CodeCountry, 
                Id, 
                Count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.connection.cursor()  
        try:
            for entry in json_data:  
                prefix = str(entry.get("prefix"))
                count = str(entry.get("count"))

                for instance in entry.get("instances", []):
                    marker = instance.get("marker", {})
                    
                    longitude = str(marker.get("longitude"))
                    latitude = str(marker.get("latitude"))
                    city = str(marker.get("city"))
                    code_country = str(marker.get("code_country"))
                    location_id = str(marker.get("id"))

                    values = (
                        prefix,       
                        date,        
                        longitude,    
                        latitude,     
                        city,         
                        code_country, 
                        location_id,  
                        count         
                    )

                    cursor.execute(sql_insert_query, values)

          
            self.connection.commit()
            print(f"Inserted {len(json_data)} records into LocationIPv6 table.")

        except Error as e:
            print(f"Error inserting into LocationIPv6 table: {e}")
        finally:
            cursor.close()  

    def insert_location_ipv4(self, json_data, date):
        """Inserts location data for IPv4 into the database."""
        
        sql_insert_query = """
            INSERT INTO LocationIPv4 (
                Prefix, 
                Date, 
                Longitude, 
                Latitude, 
                City, 
                CodeCountry, 
                Id, 
                Count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.connection.cursor()  
        try:
            for entry in json_data:  
                prefix = str(entry.get("prefix"))
                count = str(entry.get("count"))

                for instance in entry.get("instances", []):
                    marker = instance.get("marker", {})
                    longitude = str(marker.get("longitude"))
                    latitude = str(marker.get("latitude"))
                    city = str(marker.get("city"))
                    code_country = str(marker.get("code_country"))
                    location_id = str(marker.get("id"))

                    values = (
                        prefix,       
                        date,         
                        longitude,   
                        latitude,     
                        city,        
                        code_country, 
                        location_id,  
                        count         
                    )

                    
                    cursor.execute(sql_insert_query, values)

            self.connection.commit()
            print(f"Inserted {len(json_data)} records into LocationIPv4 table.")

        except Error as e:
            print(f"Error inserting into LocationIPv4 table: {e}")
        finally:
            cursor.close()  

