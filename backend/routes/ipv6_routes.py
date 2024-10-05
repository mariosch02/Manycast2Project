from flask import Blueprint, jsonify, request, current_app

ipv6_bp = Blueprint('ipv6', __name__)

@ipv6_bp.route('/api/ipv6/<date>/<prefix>', methods=['GET'])
def get_all_ipv6_date(date, prefix):
    """Retrieve all IPv6 addresses for a given date and prefix."""
    
    db = current_app.extensions.get('db')  # Access the db instance

    connection = db.connect()
    if connection is None:
        return jsonify({"error": "Failed to connect to database"}), 500
    
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT     
                l.Prefix,
                l.Date,
                l.Longitude,
                l.Latitude,
                l.City,
                l.CodeCountry,
                l.Id,
                l.Count,
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
            WHERE i.Prefix = l.Prefix AND l.Date = ? AND l.Prefix = ?;
        """, (date, prefix))
        results = cursor.fetchall()
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()  # Close the database connection
