import json, datetime, sys
sys.path.append("..")

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from config import FlaskConfig
from models.user_model import check_email_exist, insert_user_value, get_user_id, verify_user, insert_user_request, get_user_request
# from dash_dashboard import dash_app

app = Flask(__name__)
app.config.from_object(FlaskConfig())

# @app.after_request
# def add_x_frame_options(response):
#     response.headers['X-Frame-Options'] = 'ALLOW-FROM http://localhost:8088/'
#     return response

jwt = JWTManager(app)
jwt.init_app(app)
JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)


@app.route('/')
def hello():
    return "hello"

@app.route("/api/v1/user/signup", methods=['GET','POST'])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:
            if check_email_exist(email):
                return "Email Already Exists", 403
            else:
                insert_user_value(name, email, password)
                flash("Registration Successful. Please sign in.", "success") 
                return redirect(url_for("signin"))
        
        except Exception as e:
            return f"Server Error Response: {e}", 500
        
    return render_template('signup.html')

@app.route("/api/v1/user/signin", methods=['GET','POST'])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        try:
            if verify_user(email,password) == "User not found.":
                return "Sign In Failed: User not found.", 403
            elif verify_user(email,password) == "Wrong password.":
                return "Sign In Failed: Wrong password.", 403
            elif verify_user(email,password) == "Matched.":
                user_id = get_user_id(email)
                response_data = {
                    "data": {
                        "access_token": create_access_token(identity=email),
                        "access_expired": 3600,
                        "user": {
                            "id": user_id["id"],
                            "email": email
                        }
                    }
                }
                # return redirect(url_for("profile"))
                return jsonify(response_data)
        
        except Exception as e:
            return f"Server Error Response: {e}", 500
    return render_template("signin.html")    
    
@app.route("/api/v1/user/profile", methods=['GET','POST'])
@jwt_required()
def profile():
    email = get_jwt_identity()
    user_id = get_user_id(email)
    response_data = {
        "id": user_id["id"],
        "email": email
    }
    return jsonify(response_data)

@app.route('/api/v1/user/user_request', methods=['GET','POST'])
def user_request():
    if request.method == 'POST':
        user_id = 2
        hotel_name = request.form['hotel_name']
        checkin_date = request.form['checkin_date']
        checkout_date = request.form['checkout_date']
        # print(user_id, hotel_name, checkin_date, checkout_date)
        # insert_user_request(user_id, hotel_name, checkin_date, checkout_date)

        user_request_data = get_user_request(user_id)


    return render_template("user_request.html", bookings=user_request_data)

@app.route('/dash_dashboard')
def dash_dashboard():
    return dash_app.index()

@app.route('/superset_dashboard') 
def superset_dashboard():
    return render_template('superset_dashboard.html')

@app.route("/guest-token", methods=["GET"])
def guest_token():
    url = "http://localhost:8088/api/v1/security/login" 
    payload = json.dumps({ "password": "861019", "provider": "db", "refresh": "true", "username": "Adam" })
    headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' }

    responsel = requests.request("POST", url, headers=headers, data=payload) 
    print(responsel.text)
    superset_access_token = json.loads(responsel.text)['access_token']
    payload = json.dumps ({ 
        "user": {
            "username": "Adam",
            "first_name":"Adam", 
            "last_name":"Adam"
        },
        
        "resources": [{
            "type": "dashboard",
            "id": "33757d10-61a5-4e81-a917-5e6307789969"
        }],
        "rls": []
    })
               
    bearer_token = "Bearer " + superset_access_token
    print(bearer_token)
    response2 = requests.post(
         "http://localhost:8088/api/v1/security/guest_token", 
         data = payload,
         headers = { "Authorization": bearer_token, 'Accept': 'application/json', 'Content-Type': 'application/json' }) 
    print(response2.json())
    return jsonify(response2.json()['token'])

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="127.0.0.1", debug=True)