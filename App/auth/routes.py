from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required, LoginManager
from App.server.models.user_model import User, check_email_exist, insert_user_value, get_user_info, verify_user, insert_user_request, get_user_request, delete_user_request
from App.auth import bp
from App.models import User
from flask_login import UserMixin

class User(UserMixin):
    pass

def get_user():
    return current_user

@bp.route("/")
@bp.route("/index")
@login_required
def index():
    return render_template("index.html")

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
                return redirect(url_for("auth.index"))
        
        except Exception as e:
            return f"Server Error Response: {e}", 500
    return render_template("signin.html")

@bp.route('/test', methods=['GET','POST'])
def test():
    return render_template("test.html")


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("登出成功")
    return redirect(url_for("auth.signin"))


