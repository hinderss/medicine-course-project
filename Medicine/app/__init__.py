import os
import datetime

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from disease_definer import DiseaseDefiner

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
disease_definer = DiseaseDefiner(os.getenv('DISEASES_XML'))
TODAY = datetime.date.today()

from app import routes
