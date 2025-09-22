import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("SQLALCHEMY_DATABASE_URI")
    or os.environ.get("DATABASE_URL")
    or "sqlite:///app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret")

db = SQLAlchemy()
db.init_app(app)

migrate = Migrate(app, db)
api = Api(app)
bcrypt = Bcrypt(app)
