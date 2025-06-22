import json
import os
import datetime

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from dotenv import load_dotenv

from app.agent import AgentsClient
from disease_definer import DiseaseDefiner

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')

db = SQLAlchemy(app)
ma = Marshmallow(app)
ag = AgentsClient(os.getenv('AGENTS_URL'))

login_manager = LoginManager(app)
login_manager.login_view = 'login'
disease_definer = DiseaseDefiner(os.getenv('DISEASES_XML'))
with open('diseases.json', 'r', encoding='utf-8') as file:
    diseases_json = json.load(file)
with open('symptoms.json', 'r', encoding='utf-8') as file:
    symptoms_json = json.load(file)
with open('endocrine_system.json', 'r', encoding='utf-8') as file:
    endocrine_system_json = json.load(file)
with open('vitamin_system_json.json', 'r', encoding='utf-8') as file:
    vitamin_system_json = json.load(file)
with open('micronutrients_data.json', 'r', encoding='utf-8') as file:
    micronutrients_data = json.load(file)
TODAY = datetime.date.today()
MAX_DURATION = 1440
PER_PAGE = 8
WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

from app import routes
from app import handlers
