import os
from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from flask_restful import Api, Resource
from config import db, bcrypt

from models import User, Recipe

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("SQLALCHEMY_DATABASE_URI")
    or os.environ.get("DATABASE_URL")
    or "sqlite:///app.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-secret"  

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


with app.app_context():
    db.drop_all()
    db.create_all()


class Signup(Resource):
    def post(self):
        data = request.get_json() or {}
        try:
            user = User(
                username=data.get("username"),
                image_url=data.get("image_url"),
                bio=data.get("bio"),
            )
            user.password_hash = data.get("password")
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return user.to_dict(), 201
        except Exception as e:
            return {"errors": [str(e)]}, 422


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "Unauthorized"}, 401
        return user.to_dict(), 200


class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        password = data.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session.pop("user_id")
            return "", 204
        return {"error": "Unauthorized"}, 401


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401
        recipes = Recipe.query.all()
        return [r.to_dict() for r in recipes], 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401
        data = request.get_json() or {}
        try:
            recipe = Recipe(
                title=data.get("title"),
                instructions=data.get("instructions"),
                minutes_to_complete=data.get("minutes_to_complete"),
                user_id=user_id,
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except Exception as e:
            return {"errors": [str(e)]}, 422
        

api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")

@app.get("/")
def root():
    return {"message": "Flask running"}, 200

if __name__ == "__main__":
    app.run(port=5555, debug=True)
