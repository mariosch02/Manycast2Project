from flask import Flask, jsonify, request
from flask_cors import CORS
from db.db_factory import Database 
from db.multithreading import *
from datetime import datetime
import ipaddress


db = Database()  

def create_app():
    try:
        app = Flask(__name__)
        CORS(app)


    # This function will be called hourly to insert the new data
        @app.route('/api/data', methods=['GET'])
        def get_data():
            """Handles database connection, initialization, and data update in one route."""
            connection = db.connect()
            if connection is None:
                print("Database connection failed.")
                return jsonify({"error": "Failed to connect to database"}), 500
            
            try:
                # Insert missing data to the database
                getMissingData(db, getLastDate())
                return jsonify({"message": "Database updated successfully."}), 200
            except Exception as e:
                print(f"Exception occurred: {e}")
                return jsonify({"error": f"Failed to update database: {str(e)}"}), 500
            finally:
                db.close()
    except Exception as e:
        print(f"Error in create_app(): {e}")
        return None



# This function retrieves the latest stats
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

# This provides the last stats
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
    
    # This provides the longest prefix for a specific date for an ipv4
    @app.route('/api/ipv4/<date>', methods=['GET'])
    def longest_prefix_v4(date):
        ip = request.args.get('prefix')  # Get IP from request query params
        if ip is None:
            return jsonify({"error": "IP prefix is required"}), 400

        # Database connection
        connection = db.connect()  
        if connection is None:
            return jsonify({"error": "Failed to connect to database"}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            sql_query = """
            SELECT ip.Prefix
            FROM IPAddresses ip, IPv4 v4
            WHERE v4.Date = %s
            AND v4.IPID = ip.IPID
            """
            cursor.execute(sql_query, (date,))
            results = cursor.fetchall()
            prefixes = [row['Prefix'] for row in results]
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        
      
        longest_prefix = None
        longest_prefix_length = -1
        
        try:
            ip = ipaddress.IPv4Address(ip)  
        except ipaddress.AddressValueError:
            return jsonify({"error": "Invalid IP address format"}), 400

        for prefix in prefixes:
            try:
                network = ipaddress.IPv4Network(prefix)
            except ValueError:
                continue 

            if ip in network:
                if network.prefixlen > longest_prefix_length:
                    longest_prefix = prefix
                    longest_prefix_length = network.prefixlen
        
        # if longest_prefix:
        #     return jsonify({"longest_prefix": longest_prefix}), 200
        # else:
        #     return jsonify({"message": "No matching prefix found"}), 404
        print("Longest Prefix " + longest_prefix)
        try:
            sql_query ="""
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
            cursor.execute(sql_query, (date, longest_prefix))
            result = cursor.fetchall()

            if not result:
                return jsonify({"message": "No data found for the given prefix and date"}), 404

            return jsonify(result), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close() 

    # This provides the longest prefix for a specific date for an ipv6
    @app.route('/api/ipv6/<date>', methods=['GET'])
    def longest_prefix_v6(date):
        ip = request.args.get('prefix')  # Get IP from request query params
        if ip is None:
            return jsonify({"error": "IP prefix is required"}), 400

        # Database connection
        connection = db.connect()  
        if connection is None:
            return jsonify({"error": "Failed to connect to database"}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            sql_query = """
            SELECT ip.Prefix
            FROM IPAddresses ip, IPv6 v6
            WHERE v6.Date = %s
            AND v6.IPID = ip.IPID
            """
            cursor.execute(sql_query, (date,))
            results = cursor.fetchall()
            prefixes = [row['Prefix'] for row in results]
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        
      
        longest_prefix = None
        longest_prefix_length = -1
        
        try:
            ip = ipaddress.IPv6Address(ip)  
        except ipaddress.AddressValueError:
            return jsonify({"error": "Invalid IP address format"}), 400

        for prefix in prefixes:
            try:
                network = ipaddress.IPv6Network(prefix)
            except ValueError:
                continue 

            if ip in network:
                if network.prefixlen > longest_prefix_length:
                    longest_prefix = prefix
                    longest_prefix_length = network.prefixlen
        
        print("Longest Prefix " + longest_prefix)
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
            cursor.execute(sql_query, (date, longest_prefix))
            result = cursor.fetchall()

            if not result:
                return jsonify({"message": "No data found for the given prefix and date"}), 404

            return jsonify(result), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close() 
    return app



if __name__ == "__main__":
    app = create_app()  
    if app is not None:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        print("Failed to create the Flask app.")
