from App import scheduler, mail
from flask import current_app, render_template
from flask_mail import Message
from App.server.models.hotel_model import get_request_daily_cheapest_price

import pandas as pd


@scheduler.task('interval', id='send_daily_cheapest_price_email', seconds=15)
def send_daily_cheapest_price_email():
    with current_app.app_context():
        datas = get_request_daily_cheapest_price()
        df = pd.DataFrame(datas)
        unique_emails = df['email'].unique()
        for email in unique_emails:
            filter_user_data = df[df['email'] == email]
            user_name = filter_user_data['name'].unique()[0]
            message = '...'
            # subject = "hello, %s" % data["name"]
            msg = Message('最新旅館優惠通知', sender='pricetrackertwsite@gmail.com', recipients=[email])
            msg.html = render_template('email.html', user_name=user_name, filter_user_data=filter_user_data)
            mail.send(msg)
            print(f"finsih sending email to {email}")
