import pymysql, sys
sys.path.append("/Users/chiwen/Documents/github/personal project/App/server")
from config import DatabaseConfig

con = pymysql.connect(**DatabaseConfig().db_config)

def get_request_hotel_history_price(hotel_name, checkin_date, checkout_date):
    with con.cursor() as cursor:
        SQL_get_request_hotel_history_price = """
            SELECT hotel_name, checkin_date, checkout_date, agency, twd_price, crawl_time FROM history
            WHERE hotel_name = %s AND checkin_date = %s AND checkout_date = %s
        """
        cursor.execute(SQL_get_request_hotel_history_price, (hotel_name, checkin_date, checkout_date))
        result = cursor.fetchall()
        return result

# print(get_request_hotel_history_price("APA酒店〈京成上野車站前〉", "2023-09-26", "2023-10-01"))