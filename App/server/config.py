import os, pymysql
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

class FlaskConfig:
    def __init__(self):
        # self.SECRET_KEY = os.getenv("SECRET_KEY")
        # self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        self.SECRET_KEY = "flaskverysecretkey"
        self.JWT_SECRET_KEY = "jwtverysecretkey"
        self.WTF_CSRF_EXEMPT_LIST = ['localhost', '127.0.0.1']

