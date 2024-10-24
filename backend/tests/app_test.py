import pytest
from db.db_factory import Database  

@pytest.fixture
def db():
    """Fixture to initialize the Database class."""
    return Database()

# def test_insert_and_delete_stats(db):
#     """Test inserting data into the Stats table and then deleting it."""
#     db.connect()

#     # Create separate cursors to avoid "Unread result" errors
#     insert_cursor = db.connection.cursor()
#     delete_cursor = db.connection.cursor()
#     select_cursor = db.connection.cursor()
#     # Insert test data into the Stats table
#     insert_query = """
#         INSERT INTO Stats (
#             Date, ICMPv4_GCD_Nodes, ICMPv6_GCD_Nodes, 
#             Anycast_ICMPv4_Count, Anycast_TCPv4_Count, Anycast_UDPv4_Count, 
#             GCD_ICMPv4_Count, GCD_TCPv4_Count, 
#             Anycast_ICMPv6_Count, Anycast_TCPv6_Count, Anycast_UDPv6_Count, 
#             GCD_ICMPv6_Count, GCD_TCPv6_Count
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """

#     test_date = "2024-01-01"
#     test_data = (test_date, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120)

#     insert_cursor.execute(insert_query, test_data)
#     db.connection.commit()

#     # Verify that the data was inserted correctly
#     select_cursor.execute("SELECT * FROM Stats WHERE Date = %s", (test_date,))
#     result = select_cursor.fetchone()

#     # Convert the result date to string for comparison
#     result_date = result[0].strftime("%Y-%m-%d") if result else None
#     print("This is the result date " + result_date)
#     print(test_date)

#     delete_cursor.execute("DELETE FROM Stats WHERE Date = %s", (test_date,))
#     db.connection.commit()
#     db.close()
#     assert result_date == test_date, f"Inserted date does not match: {result_date}"



# def test_longest_prefix_v4(db, client):
#     """Test the longest_prefix_v4 route by inserting and verifying the longest prefix."""
#     db.connect()

#     # Create a cursor for database operations
#     insert_cursor = db.connection.cursor()

#     # Insert test data into the IPAddresses and IPv4 tables
#     test_ip_data = [
#         ('8.8.8.0/24', 1),
#         ('8.8.4.0/22', 2)
#     ]

#     insert_ip_query = "INSERT INTO IPAddresses (Prefix, IPID) VALUES (%s, %s)"
#     for prefix, ipid in test_ip_data:
#         insert_cursor.execute(insert_ip_query, (prefix, ipid))
    
#     insert_ipv4_query = """
#         INSERT INTO IPv4 (
#             IPID, MAnycast_ICMPv4, MAnycast_TCPv4, MAnycast_UDPv4,
#             iGreedyICMPv4, iGreedyTCPv4, MAnycast_ICMPv4_Count, MAnycast_TCPv4_Count, 
#             MAnycast_UDPv4_Count, iGreedyICMPv4_Count, iGreedyTCPv4_Count, Date
#         ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """

#     test_ipv4_data = (
#         1, 'true', 'true', 'true', 'false', 'false', 1, 2, 3, 4, 5, '2024-01-01'
#     )
#     insert_cursor.execute(insert_ipv4_query, test_ipv4_data)

#     db.connection.commit()

#     # Call the API route to get the longest prefix for 8.8.8.8
#     response = client.get('/api/ipv4/2024-01-01?prefix=8.8.8.8')
#     assert response.status_code == 200
#     data = response.json
#     assert len(data) > 0, "No data returned for longest prefix"

#     # Validate that the longest prefix is correct
#     assert data[0]['Prefix'] == '8.8.8.0/24', f"Expected '8.8.8.0/24', but got {data[0]['Prefix']}"

#     # Clean up: delete the inserted test data
#     insert_cursor.execute("DELETE FROM IPAddresses WHERE Prefix IN ('8.8.8.0/24', '8.8.4.0/22')")
#     insert_cursor.execute("DELETE FROM IPv4 WHERE IPID IN (1, 2)")
#     db.connection.commit()

#     # Close the cursor and database connection
#     insert_cursor.close()
#     db.close()
