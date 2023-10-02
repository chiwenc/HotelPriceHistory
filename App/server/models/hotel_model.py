import os, pymysql, sys
sys.path.append("/Users/chiwen/Documents/github/personal project/App/server")
# from App.config import DatabaseConfig
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    def __init__(self):
        self.DB_IP = os.getenv("RDSDB_IP")
        self.DB_UserName = os.getenv("RDSDB_USERNAME")
        self.DB_Password = os.getenv("RDSDB_PASSWORD")
        self.DB_DATABASE = os.getenv("RDSDB_DATABASE")
        self.db_config = {"host": self.DB_IP,
                          "user": self.DB_UserName,
                          "password": self.DB_Password,
                          "database": self.DB_DATABASE,
                          "charset": "utf8mb4",
                          "port": 3306,
                          "cursorclass": pymysql.cursors.DictCursor,
                          "autocommit": True}

con = pymysql.connect(**DatabaseConfig().db_config)

def get_request_hotel_history_price(user_id):
    with con.cursor() as cursor:
        SQL_get_request_hotel_history_price = """
            SELECT h.hotel_name, h.checkin_date, h.checkout_date, agency, twd_price, crawl_time FROM history h
            INNER JOIN (
                SELECT hotel_name, checkin_date, checkout_date 
                FROM user_request
                WHERE user_id = %s
            ) ur
            ON h.hotel_name = ur.hotel_name AND
            h.checkin_date = ur.checkin_date AND 
            h.checkout_date = ur.checkout_date
        """
        cursor.execute(SQL_get_request_hotel_history_price, (user_id,))
        result = cursor.fetchall()
        return result

def get_hotel_all_history_price(user_id):
    with con.cursor() as cursor:
        SQL_get_hotel_all_history_price = """
            select al.hotel_name, twd_price, crawl_time from all_history al
            inner join (
	            select hotel_name from user_request
                where user_id = %s
            ) ur
            on al.hotel_name = ur.hotel_name
            order by hotel_name, crawl_time desc
        """
        cursor.execute(SQL_get_hotel_all_history_price, (user_id,))
        result = cursor.fetchall() 
        return result

# print(get_request_hotel_history_price(2))
# print(get_request_hotel_history_price("APA酒店〈京成上野車站前〉", "2023-09-26", "2023-10-01"))

# print(get_price_from_all_history("APA Hotel Machida-Eki Higashi"))