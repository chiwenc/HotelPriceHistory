from config import DatabaseConfig
from flask_bcrypt import Bcrypt
import pymysql

con = pymysql.connect(**DatabaseConfig().db_config)

def check_email_exist(email):
    with con.cursor() as cursor:
        cursor.execute("SELECT email FROM user_info WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            return True
        else:
            return False

def insert_user_value(name, email, password):
    with con.cursor() as cursor:   
        bcrypt = Bcrypt()
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8') #將密碼加密再存入資料庫
        SQL_insert_user = "INSERT INTO user_info (name, email, password) VALUES(%s,%s,%s)"
        cursor.execute(SQL_insert_user, (name, email, hashed_password))
        con.commit()
        return "Successfully registered!"

def get_user_id(email):
    with con.cursor() as cursor:
        SQL_get_user_id = "SELECT id FROM user_info WHERE email = %s"
        cursor.execute(SQL_get_user_id, (email,))
        user_id = cursor.fetchone()
        return user_id

def verify_user(email, password):   
    with con.cursor() as cursor:
        cursor.execute("SELECT password FROM user_info WHERE email = %s", (email,))
        result = cursor.fetchone()
        print(result)
        if not result:
            return "User not found."
        
        hashed_password = result["password"]
        bcrypt = Bcrypt()
        if bcrypt.check_password_hash(hashed_password, password):
            return "Matched."
        else:
            return "Wrong password."