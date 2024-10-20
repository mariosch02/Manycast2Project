import mysql.connector
from mysql.connector import Error
from config import *  # Assuming config.py contains DATABASE_CONFIG and other necessary variables
import os
import json
import gc
from multiprocessing import Pool

class Database:
    """Database class to manage the MySQL database connection."""

    def __init__(self):
        self.connection = None

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
                CREATE TABLE IF NOT EXISTS IPAddresses (
                    IPID INT AUTO_INCREMENT PRIMARY KEY,  
                    Prefix VARCHAR(45) UNIQUE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS IPv4 (
                    IPID INT,
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
                    Date TEXT,
                    FOREIGN KEY (IPID) REFERENCES IPAddresses(IPID) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS IPv6 (
                    IPID INT,
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
                    Date TEXT,
                    FOREIGN KEY (IPID) REFERENCES IPAddresses(IPID) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS LocationIPv4 (
                    IPID INT,
                    Date TEXT,
                    Longitude FLOAT,
                    Latitude FLOAT,
                    City VARCHAR(100),
                    CodeCountry VARCHAR(10),
                    Id TEXT,
                    Count INT,
                    FOREIGN KEY (IPID) REFERENCES IPAddresses(IPID) ON DELETE CASCADE
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS LocationIPv6 (
                    IPID INT,
                    Date TEXT,
                    Longitude FLOAT,
                    Latitude FLOAT,
                    City VARCHAR(100),
                    CodeCountry VARCHAR(10),
                    Id TEXT,
                    Count INT,
                    FOREIGN KEY (IPID) REFERENCES IPAddresses(IPID) ON DELETE CASCADE
                );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS Stats (
            Date DATE,                            
            ICMPv4_GCD_Nodes INT,               
            ICMPv6_GCD_Nodes INT,                 
            Anycast_ICMPv4_Count INT,             
            Anycast_TCPv4_Count INT,             
            Anycast_UDPv4_Count INT,            
            GCD_ICMPv4_Count INT,                
            GCD_TCPv4_Count INT,               
            Anycast_ICMPv6_Count INT,             
            Anycast_TCPv6_Count INT,              
            Anycast_UDPv6_Count INT,             
            GCD_ICMPv6_Count INT,                
            GCD_TCPv6_Count INT                  
            );
            """)

            cursor.execute("""
                 CREATE TABLE ProcessedFiles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );""")
            self.connection.commit()
            print("SQL tables created successfully.")
        except Error as e:
            print(f"Error executing query: {e}")
        finally:
            cursor.close()

    def disable_foreign_key_checks(self):
        """Disables foreign key checks temporarily."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("SET foreign_key_checks = 0;")
            print("Foreign key checks disabled.")
        except Error as e:
            print(f"Error disabling foreign key checks: {e}")
        finally:
            cursor.close()

    def enable_foreign_key_checks(self):
        """Re-enables foreign key checks after inserts."""
        cursor = self.connection.cursor()
        try:
            cursor.execute("SET foreign_key_checks = 1;")
            print("Foreign key checks enabled.")
        except Error as e:
            print(f"Error enabling foreign key checks: {e}")
        finally:
            cursor.close()

    def get_or_insert_ipid(self, prefix, cursor, connection):
        """Retrieve the IPID for a given prefix or insert it if it doesn't exist."""
        try:
            cursor.execute("SELECT IPID FROM IPAddresses WHERE Prefix = %s", (prefix,))
            result = cursor.fetchone()

            if result:
                return result[0]  # Return the existing IPID
            else:
                cursor.execute("INSERT INTO IPAddresses (Prefix) VALUES (%s)", (prefix,))
                connection.commit()
                new_ipid = cursor.lastrowid
                return new_ipid
        except Error as e:
            print(f"Error getting or inserting IPID for {prefix}: {e}")
            return None

    def process_file_mp(self, file_path):
        """Processes a single JSON file and inserts its data into the database using multiprocessing."""
        # Establish a new database connection for each process
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        try:
            with open(file_path, 'r') as file:
                filename = os.path.basename(file_path)
                date = filename[:10]
                version = filename[11:13]
                location = len(filename) > 18
                json_data = json.load(file)

                if not location and version == "v6":
                    print(f"Inserting IPv6 data from {file_path}")
                    self.insert_v6(json_data, date, cursor, connection)
                elif not location and version == "v4":
                    print(f"Inserting IPv4 data from {file_path}")
                    self.insert_v4(json_data, date, cursor, connection)
                elif location and version == "v6":
                    print(f"Inserting IPv6 location data from {file_path}")
                    self.insert_location_ipv6(json_data, date, cursor, connection)
                elif location and version == "v4":
                    print(f"Inserting IPv4 location data from {file_path}")
                    self.insert_location_ipv4(json_data, date, cursor, connection)

            connection.commit()
            print(f"File {file_path} committed.")

        except mysql.connector.Error as err:
            print(f"Error processing file {file_path}: {err}")
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file {file_path}: {e}")
        except Exception as e:
            print(f"An error occurred with file {file_path}: {e}")
        finally:
            cursor.close()
            connection.close()
            print(f"Database connection for file {file_path} closed.")

    def update_daily_database_multiprocessing(self, num_processes=4):
        """Updates the daily database using multiprocessing."""
        TEST_LOCAL_REPO_PATH = './anycast-census/2024'
        print(f"Looking for JSON files in directory: {TEST_LOCAL_REPO_PATH}")

        # Collect all JSON files to process
        files_to_process = []
        for dirpath, dirnames, filenames in os.walk(TEST_LOCAL_REPO_PATH):
            for filename in filenames:
                if filename.endswith(".json"):
                    file_path = os.path.join(dirpath, filename)
                    files_to_process.append(file_path)

        total_files = len(files_to_process)
        print(f"Found {total_files} JSON files to process.")

        # Use multiprocessing to process files
        with Pool(num_processes) as pool:
            pool.map(self.process_file_mp, files_to_process)

        print("Completed processing all JSON files.")

    # Insert methods with batch insertion
    def insert_v4(self, json_data, date, cursor, connection, batch_size=100):
        """Inserts IPv4 data into the database in batches."""
        sql_insert_query = """
            INSERT INTO IPv4(
                IPID, 
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

        records_to_insert = []
        for ipv4 in json_data:
            prefix = ipv4["prefix"]
            ipid = self.get_or_insert_ipid(prefix, cursor, connection)

            if ipid is None:
                continue

            values = (
                ipid,
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
            records_to_insert.append(values)

            # Insert in batches
            if len(records_to_insert) >= batch_size:
                cursor.executemany(sql_insert_query, records_to_insert)
                connection.commit()
                print(f"Inserted {len(records_to_insert)} IPv4 records.")
                records_to_insert = []

        # Insert any remaining records
        if records_to_insert:
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            print(f"Inserted remaining {len(records_to_insert)} IPv4 records.")

    def insert_v6(self, json_data, date, cursor, connection, batch_size=100):
        """Inserts IPv6 data into the database in batches."""
        sql_insert_query = """
            INSERT INTO IPv6(
                IPID, 
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

        records_to_insert = []
        for ipv6 in json_data:
            prefix = ipv6["prefix"]
            ipid = self.get_or_insert_ipid(prefix, cursor, connection)

            if ipid is None:
                continue

            values = (
                ipid,
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
                date
            )
            records_to_insert.append(values)

            # Insert in batches
            if len(records_to_insert) >= batch_size:
                cursor.executemany(sql_insert_query, records_to_insert)
                connection.commit()
                print(f"Inserted {len(records_to_insert)} IPv6 records.")
                records_to_insert = []

        # Insert any remaining records
        if records_to_insert:
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            print(f"Inserted remaining {len(records_to_insert)} IPv6 records.")

    def insert_location_ipv4(self, json_data, date, cursor, connection, batch_size=100):
        """Inserts IPv4 location data into the database in batches."""
        sql_insert_query = """
            INSERT INTO LocationIPv4(
                IPID, 
                Date, 
                Longitude, 
                Latitude, 
                City, 
                CodeCountry, 
                Id, 
                Count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        records_to_insert = []
        for entry in json_data:
            prefix = entry["prefix"]
            count = entry["count"]
            ipid = self.get_or_insert_ipid(prefix, cursor, connection)

            if ipid is None:
                continue

            for instance in entry.get("instances", []):
                marker = instance.get("marker", {})
                values = (
                    ipid,
                    date,
                    str(marker.get("longitude")),
                    str(marker.get("latitude")),
                    str(marker.get("city")),
                    str(marker.get("code_country")),
                    str(marker.get("id")),
                    count
                )
                records_to_insert.append(values)

                # Insert in batches
                if len(records_to_insert) >= batch_size:
                    cursor.executemany(sql_insert_query, records_to_insert)
                    connection.commit()
                    print(f"Inserted {len(records_to_insert)} LocationIPv4 records.")
                    records_to_insert = []

        # Insert any remaining records
        if records_to_insert:
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            print(f"Inserted remaining {len(records_to_insert)} LocationIPv4 records.")

    def insert_location_ipv6(self, json_data, date, cursor, connection, batch_size=100):
        """Inserts IPv6 location data into the database in batches."""
        sql_insert_query = """
            INSERT INTO LocationIPv6(
                IPID, 
                Date, 
                Longitude, 
                Latitude, 
                City, 
                CodeCountry, 
                Id, 
                Count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        records_to_insert = []
        for entry in json_data:
            prefix = entry["prefix"]
            count = entry["count"]
            ipid = self.get_or_insert_ipid(prefix, cursor, connection)

            if ipid is None:
                continue

            for instance in entry.get("instances", []):
                marker = instance.get("marker", {})
                values = (
                    ipid,
                    date,
                    str(marker.get("longitude")),
                    str(marker.get("latitude")),
                    str(marker.get("city")),
                    str(marker.get("code_country")),
                    str(marker.get("id")),
                    count
                )
                records_to_insert.append(values)

                # Insert in batches
                if len(records_to_insert) >= batch_size:
                    cursor.executemany(sql_insert_query, records_to_insert)
                    connection.commit()
                    print(f"Inserted {len(records_to_insert)} LocationIPv6 records.")
                    records_to_insert = []

        # Insert any remaining records
        if records_to_insert:
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            print(f"Inserted remaining {len(records_to_insert)} LocationIPv6 records.")
