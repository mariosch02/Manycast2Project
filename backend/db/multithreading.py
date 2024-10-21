import mysql.connector
from mysql.connector import Error
from config import *  # Assuming config.py contains DATABASE_CONFIG and other necessary variables
import os
import json
from multiprocessing import Pool
import logging
import time
import re
import git
from datetime import datetime, timedelta
import requests
from mysql.connector import pooling
import concurrent.futures
import gc  # Python's garbage collector
import tracemalloc  # For tracking memory usage
from .db_factory import Database 
# Set up basic logging
logging.basicConfig(level=logging.INFO)


def connect_to_database():
    """Establishes a new connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**DATABASE_CONFIG)
        if connection.is_connected():
            logging.info("Database connection established.")
        return connection
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database: {err}")
        return None


def close_database_connection(connection):
    """Closes the given database connection."""
    if connection:
        connection.close()
        logging.info("Database connection closed.")


def get_or_insert_ipid(prefix, cursor, connection, ip_cache):
    """Retrieve the IPID for a given prefix from cache or database, or insert it if it doesn't exist."""
    if prefix in ip_cache:
        print("Test Cachce")
        return ip_cache[prefix]

    try:
        logging.info(f"Looking up IPID for prefix: {prefix}")
        cursor.execute("SELECT IPID FROM IPAddresses WHERE Prefix = %s", (prefix,))
        result = cursor.fetchone()
        print(f"Type: {result}")
        if result:
            print(f"Eimai dame {result.get('IPID')}")
            ipid = result.get('IPID') # Use an integer index here if result is a tuple
        else:
            print("skata")
            cursor.execute("INSERT IGNORE INTO IPAddresses (Prefix) VALUES (%s)", (prefix,))
            connection.commit()
            cursor.execute("SELECT IPID FROM IPAddresses WHERE Prefix = %s", (prefix,))
            result = cursor.fetchone()
            ipid = result.get('IPID')  # Use an integer index again

        ip_cache[prefix] = ipid  # Cache the IPID for this prefix
        print("return")
        print(ipid)
        return ipid

    except Error as e:
        logging.error(f"Error getting or inserting IPID for {prefix}: {e}")
        return None


def get_or_insert_location_ipid(prefix, cursor, connection, ip_cache):
    """Retrieve the IPID for a given prefix from cache or database, or insert it if it doesn't exist."""
    cursor = connection.cursor(dictionary=True)
    if prefix in ip_cache:
        print("Test Cachce")
        return ip_cache[prefix]

    try:
        logging.info(f"Looking up IPID for prefix: {prefix}")
        cursor.execute("SELECT IPID FROM IPAddresses WHERE Prefix = %s", (prefix,))
        result = cursor.fetchone()
        print(f"Type: {result}")
        if result:
            print(f"Eimai dame {result.get('IPID')}")
            ipid = result["IPID"] # Use an integer index here if result is a tuple
        else:
            print("skata")
            cursor.execute("INSERT IGNORE INTO IPAddresses (Prefix) VALUES (%s)", (prefix,))
            connection.commit()
            cursor.execute("SELECT IPID FROM IPAddresses WHERE Prefix = %s", (prefix,))
            result = cursor.fetchone()
            ipid =result["IPID"]  # Use an integer index again

        ip_cache[prefix] = ipid  # Cache the IPID for this prefix
        print("return")
        print(ipid)
        return ipid

    except Error as e:
        logging.error(f"Error getting or inserting IPID for {prefix}: {e}")
        return None



def close_connection(connection):
    if connection:
        connection.close()
        logging.info("Database connection closed.")




def getLastDate():
    try:
        connection = connect_to_database()
        cursor = connection.cursor(dictionary=True)  
        # Execute the query to get the most recent record from the IPv4 table
        cursor.execute("""
            SELECT Date
            FROM IPv6
            ORDER BY Date DESC
        """)
        # Last Date
        latest_entry = cursor.fetchone()
        if (latest_entry == None):
            latest_entry = "2024-03-21"
            return latest_entry
        if latest_entry:
            print(f"Latest IPv4 entry: {latest_entry['Date']}")
            return latest_entry['Date']
        else:
            return "No entries found in the database."
    except mysql.connector.Error as error:
        print(f"Error fetching the latest entry: {error}")
        return None

def getMissingData(db, start_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() 
    today = datetime.now().date()  
    current_date = start_date
    db.initialize_database()
    print("This is called")
    while current_date <= today:
        date_str = current_date.strftime("%Y-%m-%d")
        # fetch_github_data_v4(date_str)
        # fetch_github_data_location_v4(date_str)
        fetch_github_data_v6(date_str)
        # fetch_github_data_location_v6(date_str)
        # fetch_github_stats(date_str)
        current_date += timedelta(days=1)


def fetch_github_stats(date_str):
    # Convert the GitHub URL to raw URL
    year = date_str[0:4]
    month = date_str[5:7]
    day = date_str[8:10]
    print(date_str)
    url = f"https://raw.githubusercontent.com/anycast-census/anycast-census/main/{year}/{month}/{day}/stats"
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    try:
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Data retrieved successfully from {url}")
            print("Response text" + response.text)
            insert_stats(response.text, date_str, cursor, connection)
            return response.text  # Return the file content as text
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None




def fetch_github_data_v4(date_str):
    year = date_str[0:4]
    month = date_str[5:7]
    day = date_str[8:10]
    base_url = f"https://raw.githubusercontent.com/anycast-census/anycast-census/main/{year}/{month}/{day}/{date_str}_v4.json"
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    try:
        # Send a GET request to the raw GitHub URL
        response = requests.get(base_url)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Data for {date_str} retrieved successfully.")
            try :
                json_data = response.json()  # Parse the response as JSON
                # print(json_data)
                insert_data_v4(json_data, date_str, cursor, connection)
            except ValueError:
                print(f"Error: Could not parse JSON for {date_str}. Response might not be JSON.")
                return None
        else:
            print(f"Failed to fetch data for {date_str}. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None
    
def fetch_github_data_location_v4(date_str):
    year = date_str[0:4]
    month = date_str[5:7]
    day = date_str[8:10]
    base_url = f"https://raw.githubusercontent.com/anycast-census/anycast-census/main/{year}/{month}/{day}/{date_str}_v4_locations.json"
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            # print(f"Data for {date_str} retrieved successfully.")
            json_data = response.json()  
            # print(json_data)
            insert_location_v4(json_data,date_str)
            # return "Data is being inserted"
        else:
            print(f"For {date_str}. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None

def fetch_github_data_v6(date_str):
    year = date_str[0:4]
    month = date_str[5:7]
    day = date_str[8:10]
    base_url = f"https://raw.githubusercontent.com/anycast-census/anycast-census/main/{year}/{month}/{day}/{date_str}_v6.json"
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    try:
        # Send a GET request to the raw GitHub URL
        response = requests.get(base_url)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Data for {date_str} retrieved successfully.")
            json_data = response.json()  # Parse the response as JSON
            insert_data_v6(json_data, date_str, cursor, connection)
            return "Data is being inserted"
        else:
            print(f"Failed to fetch data for {date_str}. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None

def fetch_github_data_location_v6(date_str):
    year = date_str[0:4]
    month = date_str[5:7]
    day = date_str[8:10]
    base_url = f"https://raw.githubusercontent.com/anycast-census/anycast-census/main/{year}/{month}/{day}/{date_str}_v6_locations.json"
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    try:
        # Send a GET request to the raw GitHub URL
        response = requests.get(base_url)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Data for {date_str} retrieved successfully.")
            json_data = response.json()  # Parse the response as JSON
            insert_location_v6(json_data,date_str)
            return "Data is being inserted"
        else:
            print(f"Failed to fetch data for {date_str}. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred while fetching data: {e}")
        return None
    finally:
        close_connection(connection)




def insert_stats(stats_data, date, cursor, connection):
    """
    Inserts the statistics data from the stats file into the Stats table.
    """
    # Extract stats using regex from the stats_data text
    stats_dict = {
        "ICMPv4_GCD_Nodes": int(re.search(r'ICMPv4 GCD nodes:\s*(\d+)', stats_data).group(1)),
        "ICMPv6_GCD_Nodes": int(re.search(r'ICMPv6 GCD nodes:\s*(\d+)', stats_data).group(1)),
        "Anycast_ICMPv4_Count": int(re.search(r'Anycast-based ICMPv4:\s*(\d+)', stats_data).group(1)),
        "Anycast_TCPv4_Count": int(re.search(r'Anycast-based TCPv4:\s*(\d+)', stats_data).group(1)),
        "Anycast_UDPv4_Count": int(re.search(r'Anycast-based UDPv4:\s*(\d+)', stats_data).group(1)),
        "GCD_ICMPv4_Count": int(re.search(r'GCD-based ICMPv4:\s*(\d+)', stats_data).group(1)),
        "GCD_TCPv4_Count": int(re.search(r'GCD-based TCPv4:\s*(\d+)', stats_data).group(1)),
        "Anycast_ICMPv6_Count": int(re.search(r'Anycast-based ICMPv6:\s*(\d+)', stats_data).group(1)),
        "Anycast_TCPv6_Count": int(re.search(r'Anycast-based TCPv6:\s*(\d+)', stats_data).group(1)),
        "Anycast_UDPv6_Count": int(re.search(r'Anycast-based UDPv6:\s*(\d+)', stats_data).group(1)),
        "GCD_ICMPv6_Count": int(re.search(r'GCD-based ICMPv6:\s*(\d+)', stats_data).group(1)),
        "GCD_TCPv6_Count": int(re.search(r'GCD-based TCPv6:\s*(\d+)', stats_data).group(1))
    }

    cursor.execute("SELECT * FROM Stats WHERE Date = %s", (date,))
    if cursor.fetchone():
        print(f"Stats for {date} already exist. Skipping insertion.")
        return

    sql_insert_query = """
    INSERT INTO Stats (
        Date, ICMPv4_GCD_Nodes, ICMPv6_GCD_Nodes, 
        Anycast_ICMPv4_Count, Anycast_TCPv4_Count, Anycast_UDPv4_Count, 
        GCD_ICMPv4_Count, GCD_TCPv4_Count, 
        Anycast_ICMPv6_Count, Anycast_TCPv6_Count, Anycast_UDPv6_Count, 
        GCD_ICMPv6_Count, GCD_TCPv6_Count
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql_insert_query, (
        date,
        stats_dict["ICMPv4_GCD_Nodes"], stats_dict["ICMPv6_GCD_Nodes"],
        stats_dict["Anycast_ICMPv4_Count"], stats_dict["Anycast_TCPv4_Count"], stats_dict["Anycast_UDPv4_Count"],
        stats_dict["GCD_ICMPv4_Count"], stats_dict["GCD_TCPv4_Count"],
        stats_dict["Anycast_ICMPv6_Count"], stats_dict["Anycast_TCPv6_Count"], stats_dict["Anycast_UDPv6_Count"],
        stats_dict["GCD_ICMPv6_Count"], stats_dict["GCD_TCPv6_Count"]
    ))
    connection.commit()
    print(f"Inserted stats for {date} into the Stats table.")



def insert_data_v4(json_data, date, cursor, connection, batch_size=500):
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
    ip_cache = {}
    for ipv4 in json_data:
        # print("malaka " + str(ipv4["characterization"]))
        prefix = ipv4["prefix"]
        print("ALL PREFIX " + prefix)
        ipid = get_or_insert_ipid(prefix, cursor, connection, ip_cache)
        print(ipid)
        if ipid is None:
            print("Traoule")
            continue
        print("malaka")
        print(ipv4["characterization"])
        values = (
            int(ipid),
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

        print(f"Inserting record: {values}")
        records_to_insert.append(values)

        # if len(records_to_insert) >= batch_size:
        #     try:
        cursor.executemany(sql_insert_query, records_to_insert)
        connection.commit()
            # except mysql.connector.Error as err:
            #     print(f"Error inserting records: {err}")
            #     print(f"Failed record batch: {records_to_insert}")
        print(f"Inserted {len(records_to_insert)} IPv4 records.")
        records_to_insert = []

    if records_to_insert:
        cursor.executemany(sql_insert_query, records_to_insert)
        connection.commit()
        print(f"Inserted remaining {len(records_to_insert)} IPv4 records.")

def insert_data_v6(json_data, date, cursor, connection, batch_size=100):
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
    ip_cache = {}
    for ipv6 in json_data:
        prefix = ipv6["prefix"]
        ipid = get_or_insert_ipid(prefix, cursor, connection, ip_cache)

        if ipid is None:
            continue

        values = (
            int(ipid),
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

        if len(records_to_insert) >= batch_size:
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            print(f"Inserted {len(records_to_insert)} IPv6 records.")
            records_to_insert = []

    if records_to_insert:
        cursor.executemany(sql_insert_query, records_to_insert)
        connection.commit()
        print(f"Inserted remaining {len(records_to_insert)} IPv6 records.")


def insert_location_v4(json_data, date, batch_size=250):
    """Inserts IPv4 location data into the database in smaller batches."""
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
    connection = connect_to_database()
    if not connection:
        return

    cursor = connection.cursor()

    records_to_insert = []
    ip_cache = {}  # Cache for prefixes to avoid repeated lookups
    try:
        logging.info("Starting batch insert...")
        for entry in json_data:
            prefix = entry["prefix"]
            ipid = get_or_insert_location_ipid(prefix, cursor, connection, ip_cache)

            if ipid is None:
                continue

            for instance in entry.get("instances", []):
                marker = instance.get("marker", {})
                values = (
                    ipid,
                    date,
                    float(marker.get("longitude")),
                    float(marker.get("latitude")),
                    str(marker.get("city")),
                    str(marker.get("code_country")),
                    str(marker.get("id")),
                    entry["count"]
                )
                records_to_insert.append(values)
                logging.info(f"Values  {values}")

                # Log the number of appended records
                logging.info(f"Records appended: {len(records_to_insert)}")

                # Insert in batches when the batch size is reached
                if len(records_to_insert) >= batch_size:
                    logging.info(f"Reached batch size {batch_size}, inserting records...")
                    cursor.executemany(sql_insert_query, records_to_insert)
                    connection.commit()
                    logging.info(f"Inserted {len(records_to_insert)} LocationIPv4 records.")
                    records_to_insert = []  # Clear the records to release memory

                    # Force garbage collection to free memory
                    gc.collect()

        # Insert any remaining records
        if records_to_insert:
            logging.info(f"Inserting remaining records: {len(records_to_insert)}")
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            logging.info(f"Inserted remaining {len(records_to_insert)} LocationIPv4 records.")

    except Error as e:
        logging.error(f"Error inserting location data: {e}")

    finally:
        cursor.close()
        close_database_connection(connection)
        # Run garbage collection at the end of the process
        gc.collect()


def insert_location_v6(json_data, date, batch_size=250):
    """Inserts IPv6 location data into the database in smaller batches."""
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
    connection = connect_to_database()
    if not connection:
        return

    cursor = connection.cursor()

    records_to_insert = []
    ip_cache = {}  # Cache for prefixes to avoid repeated lookups
    try:
        logging.info("Starting batch insert...")
        for entry in json_data:
            prefix = entry["prefix"]
            ipid = get_or_insert_location_ipid(prefix, cursor, connection, ip_cache)

            if ipid is None:
                continue

            for instance in entry.get("instances", []):
                marker = instance.get("marker", {})
                values = (
                    ipid,
                    date,
                    float(marker.get("longitude")),
                    float(marker.get("latitude")),
                    str(marker.get("city")),
                    str(marker.get("code_country")),
                    str(marker.get("id")),
                    entry["count"]
                )
                records_to_insert.append(values)
                logging.info(f"Values  {values}")

                # Log the number of appended records
                logging.info(f"Records appended: {len(records_to_insert)}")

                # Insert in batches when the batch size is reached
                if len(records_to_insert) >= batch_size:
                    logging.info(f"Reached batch size {batch_size}, inserting records...")
                    cursor.executemany(sql_insert_query, records_to_insert)
                    connection.commit()
                    logging.info(f"Inserted {len(records_to_insert)} LocationIPv4 records.")
                    records_to_insert = []  # Clear the records to release memory

                    # Force garbage collection to free memory
                    gc.collect()

        # Insert any remaining records
        if records_to_insert:
            logging.info(f"Inserting remaining records: {len(records_to_insert)}")
            cursor.executemany(sql_insert_query, records_to_insert)
            connection.commit()
            logging.info(f"Inserted remaining {len(records_to_insert)} LocationIPv4 records.")

    except Error as e:
        logging.error(f"Error inserting location data: {e}")

    finally:
        cursor.close()
        close_database_connection(connection)
        # Run garbage collection at the end of the process
        gc.collect()