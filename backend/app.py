from flask import Flask, jsonify, request
from flask_cors import CORS
from db.db_factory import Database 
from db.multithreading import *
from datetime import datetime


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

        @app.route('/api/ipv4/<date>', methods=['GET'])
        def get_all_ipv4(date):
            """Fetch all IPv4 data for the specified date and prefix."""
            print("Prefix " + date)
            prefix = request.args.get('prefix')

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

        @app.route('/api/ipv6/<date>', methods=['GET'])
        def get_all_ipv6(date):
            """Fetch all IPv6 data for the specified date and prefix."""
            prefix = request.args.get('prefix')

            # Debugging information
            print("test")
            print(f"Prefix: {prefix}")

            # Database connection
            try:
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
                        FROM LocationIPv6 l, IPv6 i, IPAddresses ip
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
                    cursor.close()  # Close the cursor after use

            except Exception as e:
                return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

            finally:
                if connection:
                    connection.close()  # Close the connection after the request completes

    except Exception as e:
        print(f"Error in create_app(): {e}")
        return None




    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Fetch all Stats data for the specified date """
        connection = db.connect()  
        if connection is None:
            return jsonify({"error": "Failed to connect to database"}), 500

        cursor = connection.cursor(dictionary=True) 
        try:
            sql_query = """
            SELECT 
                Anycast_ICMPv4_Count AS MAnycastICMPv4,
                Anycast_ICMPv6_Count AS MAnycastICMPv6,
                Anycast_TCPv4_Count AS MAnycastTCPv4,
                Anycast_TCPv6_Count AS MAnycastTCPv6,
                Anycast_UDPv4_Count AS MAnycastUDPv4,
                Anycast_UDPv6_Count AS MAnycastUDPv6,
                GCD_ICMPv4_Count AS iGreedyICMPv4,
                GCD_ICMPv6_Count AS iGreedyICMPv6,
                GCD_TCPv4_Count AS iGreedyTCPv4,
                GCD_TCPv6_Count AS iGreedyTCPv6,
                Date AS Date
            FROM Stats
            """
            cursor.execute(sql_query)
            result = cursor.fetchall()

            if not result:
                return jsonify({"message": f"No data found for the given date {date}"}), 404

            response = {}
            for i in result:
                response[str(i["Date"])] = {"MAnycastICMPv4" : str(i["MAnycastICMPv4"]),
                                            "MAnycastICMPv6" : str(i["MAnycastICMPv6"]),
                                            "MAnycastTCPv4" : str(i["MAnycastTCPv4"]),
                                            "MAnycastTCPv6" : str(i["MAnycastTCPv6"]),
                                            "MAnycastUDPv4" : str(i["MAnycastUDPv4"]),
                                            "MAnycastUDPv6" : str(i["MAnycastUDPv6"]),
                                            "iGreedyICMPv4" : str(i["iGreedyICMPv4"]),
                                            "iGreedyICMPv6" : str(i["iGreedyICMPv6"]),
                                            "iGreedyTCPv4" : str(i["iGreedyTCPv4"]),
                                            "iGreedyTCPv6" : str(i["iGreedyTCPv6"])}
            return response, 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()  
            db.close()

    @app.route('/api/stats/last', methods=['GET'])
    def get_statsDate():
        """Fetch all Stats data for the specified date """
        connection = db.connect()  
        if connection is None:
            return jsonify({"error": "Failed to connect to database"}), 500

        cursor = connection.cursor(dictionary=True) 
        try:
            sql_query = """
            SELECT Date
            FROM Stats
            ORDER BY Date DESC
            LIMIT 1;
            """
            cursor.execute(sql_query)
            result = cursor.fetchone()
            # date_str = str(result) # Extract the first (and only) string from the list
            formatted_date = result['Date'].strftime("%Y-%m-%d")
            return str(formatted_date)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()  
            db.close()
    
    
    return app



if __name__ == "__main__":
    app = create_app()  
    if app is not None:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to create the Flask app.")
