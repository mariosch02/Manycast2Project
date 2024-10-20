from flask import Flask, jsonify
from flask_cors import CORS
from db.db_factory import Database 
from db.multithreading import *

db = Database()  # Ensure db is instantiated correctly

def create_app():
    try:
        app = Flask(__name__)
        CORS(app)

        @app.route('/api/', methods=['GET'])
        def das():
            return "test"

        @app.route('/api/data', methods=['GET'])
        def get_data():
            """Handles database connection, initialization, and data update in one route."""
            connection = db.connect()
            if connection is None:
                print("Database connection failed.")
                return jsonify({"error": "Failed to connect to database"}), 500
            
            try:
                # db.initialize_database()
                # update_daily_database_multiprocessing()
                # update_database_daily()
                # getLastDate()
                getMissingData(db, getLastDate())
                return jsonify({"message": "Database updated successfully."}), 200
            except Exception as e:
                print(f"Exception occurred: {e}")
                return jsonify({"error": f"Failed to update database: {str(e)}"}), 500
            finally:
                db.close()

        @app.route('/api/ipv4/<date>/<path:prefix>', methods=['GET'])
        def get_all_ipv4(date, prefix):
            """Fetch all IPv4 data for the specified date and prefix."""
            print("Prefix " + date)
            connection = db.connect()  
            if connection is None:
                return jsonify({"error": "Failed to connect to database"}), 500

            cursor = connection.cursor(dictionary=True)  
            try:
                sql_query = """
            SELECT     
            ip.Prefix,
            l.Date,
            l.Longitude,
            l.Latitude,
            l.City,
            l.CodeCountry,
            l.Id,
            i.MAnycast_ICMPv4,
            i.MAnycast_TCPv4,
            i.MAnycast_UDPv4,
            i.iGreedyICMPv4,
            i.iGreedyTCPv4,
            i.MAnycast_ICMPv4_Count,
            i.MAnycast_TCPv4_Count,
            i.MAnycast_UDPv4_Count,
            i.iGreedyICMPv4_Count,
            i.iGreedyTCPv4_Count
            FROM LocationIPv4 l, IPv4 i, IPAddresses ip
			WHERE l.Date =  %s
            AND l.Date = i.Date
			AND l.IPID = i.IPID
            AND ip.IPID = l.IPID
            AND ip.IPID = i.IPID
            AND ip.Prefix = %s
                """
                cursor.execute(sql_query, (date, prefix))
                result = cursor.fetchall()
                if not result:
                    return jsonify({"message": "No data found for the given prefix and date"}), 404

                return jsonify(result), 200

            except Exception as e:
                return jsonify({"error": str(e)}), 500
            finally:
                cursor.close()  
                db.close()  

        @app.route('/api/ipv6/<date>/<path:prefix>', methods=['GET'])
        def get_all_ipv6(date, prefix):
            """Fetch all IPv6 data for the specified date and prefix."""
            print("Prefix " + date)
            connection = db.connect()  
            if connection is None:
                return jsonify({"error": "Failed to connect to database"}), 500

            cursor = connection.cursor(dictionary=True) 
            try:
                sql_query = """
                SELECT     
                ip.Prefix,
                l.Date,
                l.Longitude,
                l.Latitude,
                l.City,
                l.CodeCountry,
                l.Id,
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
                FROM LocationIPv6 l
                JOIN IPv6 i ON l.IPID = i.IPID
                JOIN IPAddresses ip ON ip.IPID = l.IPID
                WHERE l.Date = %s AND ip.Prefix = %s
                """
                cursor.execute(sql_query, (date, prefix))
                result = cursor.fetchall()

                if not result:
                    return jsonify({"message": "No data found for the given prefix and date"}), 404

                return jsonify(result), 200

            except Exception as e:
                return jsonify({"error": str(e)}), 500
            finally:
                cursor.close()  
                db.close()
        
        return app  # Ensure the app is returned here
    except Exception as e:
        print(f"Error in create_app(): {e}")
        return None


if __name__ == "__main__":
    app = create_app()  
    if app is not None:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to create the Flask app.")
