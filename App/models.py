import pymysql

from App import login_manager
from flask_login import UserMixin, current_user
from App.config import DatabaseConfig

con = pymysql.connect(**DatabaseConfig().db_config)


def get_user_info(email):
    with con.cursor() as cursor:
        SQL_get_user_id = "SELECT id, name FROM user_info WHERE email = %s"
        cursor.execute(SQL_get_user_id, (email,))
        user_id = cursor.fetchone()
        return user_id


class User(UserMixin):
    pass

@login_manager.user_loader
def load_user(email):
    user = User()
    user_info = get_user_info(email)
    user.id = str(user_info["id"])
    user.name = user_info["name"]
    return user

