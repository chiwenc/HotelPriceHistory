# from flask import Flask
# from config import FlaskConfig
# from dotenv import load_dotenv
# import os
# from flask_login import LoginManager

# load_dotenv()

# login_manager = LoginManager()
# login_manager.login_view = 'signin'

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(FlaskConfig())
#     login_manager.init_app()

#     from App.auth import bp as auth_bp
#     app.register_blueprint(auth_bp)

#     return app
