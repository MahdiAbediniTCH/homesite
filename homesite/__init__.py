from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '4ab5de00769c57a11253a800b8d52c76'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = "/protected/shared_files"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'لطفا برای دسترسی به صفحه مورد نظر وارد شوید.'
SITENAME = "درگاه خانگی"
SIGNUP_KEY = "_kelide-sabtenam"


from homesite import routes
