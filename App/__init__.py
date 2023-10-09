from flask import Flask, render_template
from config import FlaskConfig
from dotenv import load_dotenv
from flask_mail import Mail, Message
import os
from flask_login import LoginManager
from flask_redis import FlaskRedis
from flask_caching import Cache
from flask_apscheduler import APScheduler
from App.server.models.hotel_model import get_request_daily_cheapest_price
from datetime import datetime

import pandas as pd


load_dotenv()

mail = Mail()
scheduler = APScheduler()
login_manager = LoginManager()
login_manager.login_view = 'auth.signin'
# redis_client = FlaskRedis()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

email_batch = 1

def create_app():
    app = Flask(__name__)
    app.config.from_object(FlaskConfig())
    app.config.update(
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_DEFAULT_SENDER=('admin', 'pricetrackertwsite@gmail.com'),
        MAIL_USERNAME='pricetrackertwsite@gmail.com',
        MAIL_PASSWORD='gyffswilkurceemj'
    )
    login_manager.init_app(app)
<<<<<<< HEAD
    # redis_client.init_app(app)
    cache.init_app(app)

=======
    mail.init_app(app)
    scheduler.init_app(app)
>>>>>>> develop
    from App.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    @scheduler.task('interval', id='send_daily_cheapest_price_email', seconds=15)
    def send_daily_cheapest_price_email():
        global email_batch
        with app.app_context():
            datas = get_request_daily_cheapest_price()
            df = pd.DataFrame(datas)
            unique_emails = df['email'].unique()
            for email in unique_emails:
                print(email)
                filter_user_data = df[df['email'] == email]
                print(filter_user_data)
                user_name = filter_user_data['name'].unique()[0]
                message = '...'
                msg = Message('最新旅館優惠通知', sender='pricetrackertwsite@gmail.com', recipients=[email])
                msg.html = render_template('email.html', user_name=user_name, filter_user_data=filter_user_data)
                # mail.send(msg)
                print(f"--------------finished sending email to {email}  {datetime.now().time()}-----------------")
            print(f"-----------------finish sending batch {email_batch} {datetime.now().time()}-------------------")
            email_batch += 1

    scheduler.start()

    return app