from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_caching import Cache
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from flask_mail import Message
from App import mail
from App.server.models.user_model import User, check_email_exist, insert_user_value, get_user_info, verify_user, insert_user_request, get_user_request, delete_user_request
from App.server.models.hotel_model import get_request_hotel_history_price, get_hotel_all_history_price, search_price_history_line_chart, get_request_history_cheapest_price, get_daily_all_hotels_with_week_best_price, get_request_hotel_with_best_price
from App.auth import bp
from App.models import User
from flask_login import UserMixin
from App import cache
import pandas as pd

PAGE_SIZE = 10

class User(UserMixin):
    pass

def get_user():
    return current_user

def pagination(data_list, PAGE_SIZE, paging):
    hotels_count = len(data_list)
    total_pages = hotels_count // PAGE_SIZE
    if hotels_count % PAGE_SIZE != 0:
        total_pages += 1
    start_index = (paging-1) * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    
    result = {"total_pages": total_pages}
    
    if (hotels_count > paging * PAGE_SIZE):
        result["next_paging"] = (paging + 1)
        result["hotels"] = data_list[start_index:end_index]
    else:
        result["next_paging"] = "這是最後一頁"
        result["hotels"] = data_list[start_index:hotels_count]
    
    return result


@bp.route("/", methods=['GET','POST'])
@bp.route("/index", methods=['GET','POST'])
def index():
    paging = request.values.get('paging', 1)
    paging = int(paging)

    filters = {
        "date":"2023-10-11",
        "region":request.values.get('region'),
        "min_price":request.values.get('min_price'),
        "max_price":request.values.get('max_price'),
        "is_week_best_price":request.values.get('is_week_best_price')
    }
    data_list = get_daily_all_hotels_with_week_best_price(filters)
    hotels = pagination(data_list, PAGE_SIZE, paging)
    return render_template('index.html', hotels=hotels["hotels"], next_paging=hotels["next_paging"], total_pages=hotels["total_pages"], current_page=paging)

@bp.route("/api/v1/hotel/search_price/", methods=['GET','POST'])
def get_search_hotel_history_price():
   hotel_name = request.values.get("hotel_name")
   hotels = get_request_hotel_with_best_price("2023-10-11", hotel_name)
   chart_data = search_price_history_line_chart(hotel_name)
   return render_template("search_hotel.html", hotels=hotels, chart_data=chart_data)

@bp.route("/api/v1/user/signup", methods=['GET','POST'])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            if check_email_exist(email):
                flash("Email Already Exists")
            else:
                insert_user_value(name, email, password)
                flash("Registration Successful. Please sign in.", "success") 
                return redirect(url_for("signin"))
        
        except Exception as e:
            return f"Server Error Response: {e}", 500
        
    return render_template('signup.html')


@bp.route("/api/v1/user/signin", methods=['GET','POST'])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User()
        user.id = email
        try:
            if verify_user(email,password) == "User not found.":
                flash("Sign In Failed: User not found.")
                return render_template("signin.html")
            elif verify_user(email,password) == "Wrong password.":
                flash("Sign In Failed: Wrong password.")
                return render_template("signin.html")
            elif verify_user(email,password) == "Matched.":
                login_user(user)
                flash("Login Success.")
                return redirect(url_for("auth.member_page"))
        
        except Exception as e:
            return f"Server Error Response: {e}", 500
    return render_template("signin.html")

@bp.route('/test', methods=['GET','POST'])
@login_required
def test():
    print("abc:"+current_user.id)
    return render_template("test.html")

@bp.route('/api/v1/user/user_request', methods=['GET','POST'])
@login_required
def user_request():
    
    user_id = current_user.id
    user_request_data = get_user_request(user_id)

    if request.method == 'POST':
        user_id = current_user.id
        hotel_name = request.form['hotel_name']
        checkin_date = request.form['checkin_date']
        checkout_date = request.form['checkout_date']
        # print(user_id, hotel_name, checkin_date, checkout_date)
        insert_user_request(user_id, hotel_name, checkin_date, checkout_date)

        user_request_data = get_user_request(user_id)

    return render_template("user_request.html", bookings=user_request_data)

@bp.route('/api/v1/user/delete_request/', methods=['GET','POST'])
def delete_request():
    request_id = request.values.get("request_id")
    delete_user_request(request_id)
    return jsonify({'message': '成功刪除'})

@bp.route('/api/v1/dashboard/single_data')
@login_required
def get_dashboard_df():
    user_id = current_user.id
    single_data = get_request_hotel_history_price(user_id)
    return single_data

@bp.route('/api/v1/dashboard/all_data')
@login_required
def get_dashboard_all_df():
    user_id = current_user.id
    all_data = get_hotel_all_history_price(user_id)
    return all_data

@bp.route("/api/v1/hotel/week_best_price/", methods=['GET','POST'])
# @cache.cached(timeout=3600)
def week_best_price():
    return render_template("week_best_price.html")

# @bp.route("/api/v1/hotel/get_week_best_price/", methods=['GET','POST'])
# def search_week_best_price():
#     paging = request.values.get('paging', 1)
#     paging = int(paging)
#     region = request.values.get('region', None)    
#     data_list = get_daily_all_hotels_with_week_best_price("2023-10-07",region)
#     result = pagination(data_list, PAGE_SIZE, paging)
#     # result = {"hotels": data_list}
    
#     return jsonify(result)

@bp.route("/api/v1/hotel/get_request_hotel_info")
def search_request_hotel():
    hotel_name = request.values.get("hotel_name")
    hotel_data = get_request_hotel_with_best_price("2023-10-11",hotel_name)
    chart_data = search_price_history_line_chart(hotel_name)
    return {
        "hotel_data": hotel_data[0],
        "chart_data": chart_data
    }

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("登出成功")
    return redirect(url_for("auth.signin"))

@bp.route('/email')
def send_email():
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
        print(mail)
        mail.send(msg)
    return datas

@bp.route('/notification/request_history_cheapest_price')
def email_history_cheapest_price():
    datas = get_request_history_cheapest_price()
    df = pd.DataFrame(datas)
    unique_emails = df['email'].unique()
    for email in unique_emails:
        filter_user_data = df[df['email'] == email]
        user_name = filter_user_data['name'].unique()[0]
        # subject = "hello, %s" % data["name"]
        msg = Message('旅館歷史最低價通知', sender='pricetrackertwsite@gmail.com', recipients=[email])
        msg.html = render_template('email.html', user_name=user_name, filter_user_data=filter_user_data)
        print(mail)
        mail.send(msg)
    return datas

@bp.route('/memberpage')
@login_required
def member_page():
    user_id = current_user.id
    data = get_request_history_cheapest_price(user_id)
    return render_template('member.html', data=data)
