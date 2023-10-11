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

def search_price_history_line_chart(hotel_name):
    with con.cursor() as cursor:
        SQL_search_price_history = "SELECT date(crawl_time) as crawl_date, min(twd_price) as min_twd_price FROM all_history WHERE hotel_name = %s GROUP BY 1"
        cursor.execute(SQL_search_price_history, (hotel_name,))
        results = cursor.fetchall()
        response = {
            "crawl_time": [results[i]["crawl_date"] for i in range(len(results))],
            "twd_price": [results[i]["min_twd_price"] for i in range(len(results))]
        }
        return response

def get_week_best_price(region):
    with con.cursor() as cursor:
        if region == all or region is None:
            SQL_search_week_best_price = f"""
                select * from (
                    select region, hotel_name, min(twd_price) as min_twd_price, crawl_time from all_history
                    where date(crawl_time) >= DATE(DATE_SUB(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'), INTERVAL 6 DAY))
                    group by 1,2
                    having min_twd_price is not null
                ) hp
                where date(crawl_time) = "2023-10-11"
            """
        else:
            SQL_search_week_best_price = f"""
                select * from (
                    select region, hotel_name, min(twd_price) as min_twd_price, crawl_time from all_history
                    where date(crawl_time) >= DATE(DATE_SUB(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'), INTERVAL 6 DAY))
                    group by 1,2
                    having min_twd_price is not null
                ) hp
                where date(crawl_time) = "2023-10-11"
                and region = '{region}'
            """
        cursor.execute(SQL_search_week_best_price)
        result = cursor.fetchall()
        return result

def get_daily_all_hotels_with_week_best_price(filters:dict):
    
    date = filters.get("date")
    region = filters.get("region")
    min_price = filters.get("min_price")
    max_price = filters.get("max_price")
    is_week_best_price = filters.get("is_week_best_price")

# where date(crawl_time) >= DATE(DATE_SUB(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'), INTERVAL 6 DAY))

    with con.cursor() as cursor:
        query = f"""
            select a.region, a.hotel_name, a.crawl_time, min(a.twd_price) as min_twd_price,
                case when w.hotel_name is null then 0 else 1 end as is_week_best_price 
            from all_history a
            left join (
                select * from (
                    select region, hotel_name, crawl_time, min(twd_price) as min_twd_price from all_history
                    group by 1,2
                    having min_twd_price is not null
                ) hp
                where date(hp.crawl_time) = '{date}'
            ) w on a.hotel_name = w.hotel_name and a.region = w.region
            WHERE date(a.crawl_time) = '{date}'
        """
        if region and region != "all":
            query += f"\n  AND a.region = '{region}'"

        query += "\nGROUP BY 1, 2, 3\nHAVING min_twd_price IS NOT NULL"
        if min_price:
            query += f"\n  AND min_twd_price >= {min_price}"
        if max_price:
            query += f"\n  AND min_twd_price <= {max_price}"
        if is_week_best_price:
            query += f"\n  AND is_week_best_price = {is_week_best_price}"

        # if region == "all" or region is None:
        #     SQL_get_daily_all_hotels_with_week_best_price = f"""
        #         select a.region, a.hotel_name, a.crawl_time, min(a.twd_price) as min_twd_price
        #             ,case when w.hotel_name is null then 0 else 1 end as is_week_best_price 
        #             from all_history a
        #             left join (
        #                 select * from (
        #                     select region, hotel_name, crawl_time, min(twd_price) as min_twd_price from all_history
        #                     where date(crawl_time) >= DATE(DATE_SUB(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'), INTERVAL 6 DAY))
        #                     group by 1,2
        #                     having min_twd_price is not null
        #                 ) hp
        #                 where date(hp.crawl_time) = "{date}"
        #             ) w on a.hotel_name = w.hotel_name and a.region = w.region
        #             where date(a.crawl_time) = "{date}" 
        #             group by 1,2,3
        #             having min_twd_price is not null
        #     """
       
        cursor.execute(query)
        result = cursor.fetchall()
        return result

# print(get_daily_all_hotels_with_week_best_price("2023-10-07")[:15])

def get_request_hotel_with_best_price(date, hotel_name):
    with con.cursor() as cursor:
        SQL_get_request_hotel_with_best_price = f"""
            select a.region, a.hotel_name, a.crawl_time, min(a.twd_price) as min_twd_price
                ,case when w.hotel_name is null then 0 else 1 end as is_week_best_price 
                from all_history a
                left join (
                    select * from (
                        select region, hotel_name, crawl_time, min(twd_price) as min_twd_price from all_history
                        where date(crawl_time) >= DATE(DATE_SUB(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'), INTERVAL 6 DAY))
                        group by 1,2
                        having min_twd_price is not null
                    ) hp
                    where date(hp.crawl_time) = "{date}"
                ) w on a.hotel_name = w.hotel_name and a.region = w.region
            where date(a.crawl_time) = "{date}" and a.hotel_name = "{hotel_name}"
            group by 1,2,3
            having min_twd_price is not null
        """
        cursor.execute(SQL_get_request_hotel_with_best_price)
        result = cursor.fetchall()
        return result


def get_request_daily_cheapest_price():
    """
    拿取使用者追蹤飯店每日最便宜的價格和該價格的agency通知使用者
    """
    with con.cursor() as cursor:
        SQL_get_request_daily_cheapest_price = """
            SELECT ur.user_id, ui.name, ui.email, h.hotel_name, h.checkin_date, h.checkout_date, agency, min(twd_price) as min_twd_price, crawl_time FROM history h
            INNER JOIN (
                SELECT user_id, hotel_name, checkin_date, checkout_date 
                FROM user_request
            ) ur 
            ON h.hotel_name = ur.hotel_name AND h.checkin_date = ur.checkin_date AND h.checkout_date = ur.checkout_date
            left join user_info ui on ur.user_id = ui.id
            where date(crawl_time) = DATE(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'))
            group by hotel_name, checkin_date, checkout_date  
        """
        cursor.execute(SQL_get_request_daily_cheapest_price)
        result = cursor.fetchall()
        return result

def get_request_history_cheapest_price(user_id=None):
    """
    拿取使用者追蹤飯店今日的價格為歷史最低價的資料通知使用者
    """
    with con.cursor() as cursor:
        if not user_id:
            SQL_request_history_cheapest_price = """
                select ur.user_id, ui.name, ui.email, hp.hotel_name, hp.checkin_date, hp.checkout_date, hp.agency, hp.min_twd_price, hp.agency, hp.crawl_time
                from (
                    select hotel_name, checkin_date, checkout_date, agency, min(twd_price) as min_twd_price, crawl_time from history
                    group by hotel_name, checkin_date, checkout_date
                ) hp
                left join user_request ur on hp.hotel_name = ur.hotel_name and hp.checkin_date = ur.checkin_date and hp.checkout_date = ur.checkout_date
                left join user_info ui on ur.user_id = ui.id
                where date(crawl_time) = DATE(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'))
                and min_twd_price is not null
            """
        else:
            SQL_request_history_cheapest_price = f"""
                select ur.user_id, ui.name, ui.email, hp.hotel_name, hp.checkin_date, hp.checkout_date, hp.agency, hp.min_twd_price, hp.agency, hp.crawl_time
                from (
                    select hotel_name, checkin_date, checkout_date, agency, min(twd_price) as min_twd_price, crawl_time from history
                    group by hotel_name, checkin_date, checkout_date
                ) hp
                left join user_request ur on hp.hotel_name = ur.hotel_name and hp.checkin_date = ur.checkin_date and hp.checkout_date = ur.checkout_date
                left join user_info ui on ur.user_id = ui.id
                where min_twd_price is not null
                and ur.user_id = {user_id}
                order by hp.crawl_time desc
            """
        cursor.execute(SQL_request_history_cheapest_price)
        result = cursor.fetchall()
        return result

# print(get_request_history_cheapest_price(4))

# where date(crawl_time) = DATE(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'))
# where date(crawl_time) = DATE(DATE_SUB(CONVERT_TZ(CURDATE(), 'UTC', '+8:00'), INTERVAL 2 DAY))
