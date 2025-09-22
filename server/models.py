from sqlalchemy.orm import validates
from sqlalchemy import UniqueConstraint
from config import db, bcrypt

class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("username", name="uq_users_username"),)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String, nullable=True)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", backref="user", cascade="all, delete-orphan")

    @property
    def password_hash(self):
        raise AttributeError("Password hashes may not be viewed.")

    @password_hash.setter
    def password_hash(self, password_plaintext: str):
        if not password_plaintext or not isinstance(password_plaintext, str):
            raise ValueError("Password must be provided.")
        self._password_hash = bcrypt.generate_password_hash(password_plaintext).decode("utf-8")

    def authenticate(self, password_plaintext: str) -> bool:
        if not self._password_hash or not password_plaintext:
            return False
        return bcrypt.check_password_hash(self._password_hash, password_plaintext)

    @validates("username")
    def validate_username(self, key, value):
        if not value or not value.strip():
            raise ValueError("Username must be present.")
        return value.strip()

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "image_url": self.image_url,
            "bio": self.bio,
        }


class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    @validates("title")
    def validate_title(self, key, value):
        if not value or not value.strip():
            raise ValueError("Title must be present.")
        return value.strip()

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or not value.strip():
            raise ValueError("Instructions must be present.")
        text = value.strip()
        if len(text) < 50:
            raise ValueError("Instructions must be at least 50 characters long.")
        return text

    @validates("minutes_to_complete")
    def validate_minutes(self, key, value):
        if value is None:
            raise ValueError("Minutes to complete must be present.")
        if not isinstance(value, int) or value < 0:
            raise ValueError("Minutes to complete must be a non-negative integer.")
        return value

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "instructions": self.instructions,
            "minutes_to_complete": self.minutes_to_complete,
            "user": self.user.to_dict() if self.user else None,
        }
