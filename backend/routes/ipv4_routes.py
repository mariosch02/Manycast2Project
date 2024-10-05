# routes/ipv4_routes.py
from flask import Blueprint, jsonify, request
from app import db  # Import the db object from app.py

ipv4_bp = Blueprint('ipv4', __name__)

@ipv4_bp.route('/api/ipv4/<date>/<prefix>', methods=['GET'])
def get_all_ipv4(date, prefix):
    cursor = db.cursor(dictionary=True)  # Using dictionary=True to get results as a dict
    try:
        sql_query = """
            SELECT     
                l.Prefix,
                l.Date,
                l.Longitude,
                l.Latitude,
                l.City,
                l.CodeCountry,
                l.Id,
                i.Prefix,
                i.MAnycast_ICMPv6,
                i.MAnycast_TCPv6,
                i.MAnycast_UDPv6,
                i.iGreedyICMPv6,
                i.iGreedyTCPv6,
                i.MAnycast_ICMPv6_Count,
                i.MAnycast_TCPv6_Count,
                i.MAnycast_UDPv6_Count,
                i.iGreedyICMPv6_Count,
                i.iGreedyTCPv6_Count
            FROM LocationIPv6 l, IPv6 i
            WHERE l.Prefix = i.Prefix 
              AND l.Date = i.Date
              AND l.Prefix = %s 
              AND l.Date = %s;
        """
        # Execute the query with parameters from the URL
        cursor.execute(sql_query, (prefix, date))
        
        # Fetch all the rows returned by the query
        result = cursor.fetchall()

        # If no results found, return a 404 message
        if not result:
            return jsonify({"message": "No data found for the given prefix and date"}), 404

        # Return the result as JSON
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()  # Close the cursor
