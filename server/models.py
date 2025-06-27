from sqlalchemy import CheckConstraint
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship('Recipe', back_populates='user', cascade="all, delete")

    def __repr__(self):
        return f'<ID: {self.id} Username {self.username}>'
    
    @property
    def password_hash(self):
        raise AttributeError("Access has been denied!")
    
    @password_hash.setter
    def password(self, text):
        self._password_hash = bcrypt.generate_password_hash(text)

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)
  

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    user = db.relationship('User', back_populates='recipes')

    @validates("instructions")
    def validate_instructions(self, key, value):
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters.")
        return value

    __table_args__ = (
    CheckConstraint("length(instructions) >= 50", name="check_instructions_min_length"),
)

    def __repr__(self):
        return f'<{self.id}, {self.title}, {self.instructions}, {self.minutes_to_complete}>'
   