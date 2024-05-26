import datetime

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
TODAY = datetime.date(2024, 5, 20)

from app import routes
