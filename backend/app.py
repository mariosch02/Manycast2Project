from flask import Flask, jsonify
from flask_cors import CORS
from db.db_factory import Database  # Import the Database class

db = Database()  # Instantiate the Database class

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Import Blueprints inside the factory function to avoid circular imports



    @app.route('/api/', methods=['GET'])
    def das():
        return "test"
    @app.route('/api/data', methods=['GET'])
    def get_data():
        """Handles database connection, initialization, and data update in one route."""
        # Connect to the database
        connection = db.connect()
        if connection is None:
            return jsonify({"error": "Failed to connect to database"}), 500

        try:
            # db.initialize_database()  # Ensure the database is initialized
            # db.update_daily_database()  # Update the database with new data
            return jsonify({"message": "Database updated successfully."}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to update database: {str(e)}"}), 500
        finally:
            db.close()  # Ensure the connection is closed

    @app.route('/api/ipv6/<date>/<path:prefix>', methods=['GET'])
    def get_all_ipv6(date, prefix):
        """Fetch all IPv4 data for the specified date and prefix."""
        print("Prefix " + date)
        connection = db.connect()  # Connect to the database
        if connection is None:
            return jsonify({"error": "Failed to connect to database"}), 500

        cursor = connection.cursor(dictionary=True)  # Create a cursor
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
            WHERE l.Prefix = i.Prefix AND
            l.Date = i.Date AND
            l.Date =  %s AND
            l.Prefix = %s
            """
            # Execute the query with parameters from the URL
            cursor.execute(sql_query, (date, prefix))
            
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
            db.close()  # Ensure the connection is closed
    return app


    # @app.route('/api/ipv6/<date>/<path:prefix>', methods=['GET'])
    # def get_all_ipv6(date, prefix):
    #     """Fetch all IPv6 data for the specified date and prefix."""
    #     connection = db.connect()  # Connect to the database
    #     if connection is None:
    #         return jsonify({"error": "Failed to connect to database"}), 500

    #     cursor = connection.cursor(dictionary=True)  # Create a cursor
    #     try:
    #         sql_query = """
    #         SELECT     
    #         l.Prefix,
    #         l.Date,
    #         l.Longitude,
    #         l.Latitude,
    #         l.City,
    #         l.CodeCountry,
    #         l.Id,
    #         i.Prefix,
    #         i.MAnycast_ICMPv6,
    #         i.MAnycast_TCPv6,
    #         i.MAnycast_UDPv6,
    #         i.iGreedyICMPv6,
    #         i.iGreedyTCPv6,
    #         i.MAnycast_ICMPv6_Count,
    #         i.MAnycast_TCPv6_Count,
    #         i.MAnycast_UDPv6_Count,
    #         i.iGreedyICMPv6_Count,
    #         i.iGreedyTCPv6_Count
    #         FROM LocationIPv6 l, IPv6 i
    #         WHERE l.Prefix = i.Prefix AND
    #         l.Date = i.Date AND
    #         l.Date =  %s AND
    #         l.Prefix = %s
    #         """
    #         # Execute the query with parameters from the URL
    #         cursor.execute(sql_query, (date, prefix))
            
    #         # Fetch all the rows returned by the query
    #         result = cursor.fetchall()

    #         # If no results found, return a 404 message
    #         if not result:
    #             return jsonify({"message": "No data found for the given prefix and date"}), 404

    #         # Return the result as JSON
    #         return jsonify(result), 200

    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 500
    #     finally:
    #         cursor.close()  # Close the cursor
    #         db.close()  # Ensure the connection is closed

    # return app

if __name__ == "__main__":
    app = create_app()  # Call the factory function to create the app instance
    app.run(host='0.0.0.0', port=5000, debug=True)
