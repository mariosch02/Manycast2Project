from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import mysql.connector
from mysql.connector import Error
# from Data.dbConnection import get_db_connection
# from Data.fillData import databaseInit


app = Flask(__name__)
CORS(app)


# Connects to t
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

def databaseInit(db):
    if db is None:
        print("Error with database connectivity")
    else:
        cursor = db.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS LocationIPv4(
                    Prefix VARCHAR(45),
                    Date DATE,
                    Longitude FLOAT,
                    Latitude FLOAT,
                    City VARCHAR(100),
                    CodeCountry VARCHAR(5),
                    Id VARCHAR(255),
                    Count INT,
                    PRIMARY KEY(Date, Prefix)
                );"""
            )
            db.commit()  

            cursor.execute(       
            """CREATE TABLE IF NOT EXISTS LocationIPv6(
                    Prefix VARCHAR(45),
                    Date DATE,
                    Longitude FLOAT,
                    Latitude FLOAT,
                    City VARCHAR(100),
                    PRIMARY KEY(Date, Prefix)
                );"""
            )
            db.commit()

            cursor.execute(       
            """CREATE TABLE IF NOT EXISTS IPv4 (
                    Prefix VARCHAR(45),
                    MAnycast_ICMPv4 VARCHAR(255),
                    MAnycast_TCPv4 VARCHAR(255),
                    MAnycast_UDPv4 VARCHAR(255),
                    iGreedyICMPv4 VARCHAR(255),
                    iGreedyTCPv4 VARCHAR(255),
                    MAnycast_ICMPv4_Count INT,
                    MAnycast_TCPv4_Count INT,
                    MAnycast_UDPv4_Count INT,
                    iGreedyICMPv4_Count INT,
                    iGreedyTCPv4_Count INT,
                    Date DATE,
                    PRIMARY KEY(Prefix, Date),
                    FOREIGN KEY (Date, Prefix) REFERENCES LocationIPv4(Date, Prefix)
                );"""
            )
            db.commit() 

            cursor.execute(       
            """CREATE TABLE IF NOT EXISTS IPv6 (
                    Prefix VARCHAR(45),
                    MAnycast_ICMPv6 VARCHAR(255),
                    MAnycast_TCPv6 VARCHAR(255),
                    MAnycast_UDPv6 VARCHAR(255),
                    iGreedyICMPv6 VARCHAR(255),
                    iGreedyTCPv6 VARCHAR(255),
                    MAnycast_ICMPv6_Count INT,
                    MAnycast_TCPv6_Count INT,
                    MAnycast_UDPv6_Count INT,
                    iGreedyICMPv6_Count INT,
                    iGreedyTCPv6_Count INT,
                    Count INT,
                    CodeCountry VARCHAR(5),
                    Id VARCHAR(255),
                    Date DATE,
                    PRIMARY KEY(Prefix, Date),
                    FOREIGN KEY (Date, Prefix) REFERENCES LocationIPv6(Date, Prefix)
                );"""
            )
            db.commit()

            cursor.execute(       
            """CREATE TABLE IF NOT EXISTS Stats(
                    Date DATE PRIMARY KEY,
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
                );"""
            )
            db.commit()
            print("SQL SUCCESS")
        except Error as e:
            print(f"Error executing query: {e}")
        finally:
            cursor.close()
            db.close()  



@app.route('/api/data')
@cross_origin(origin='http://localhost:3000')
def get_data():
    connection = get_db_connection()
    databaseInit(connection)
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500
    else:
        return "SQL Connected"
    return str(connection)  
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
