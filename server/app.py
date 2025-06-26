#!/usr/bin/env python3

from flask import jsonify, make_response, request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()

            password = data.get('password')
            username = data.get('username')
            image_url = data.get('image_url')
            bio = data.get('bio')

            if not username or not password:
                return {'error': 'Username and password are required'}, 422

       
            new_user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )
            new_user.password = password

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            return make_response(jsonify({
                'id': new_user.id,
                'username': new_user.username,
                'image_url': new_user.image_url,
                'bio': new_user.bio
            }), 201)
        
        except IntegrityError:
            response_dict = {"message": "Invalid"}

            return make_response(
                jsonify(response_dict),
                422
            )

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.filter(User.id == user_id).first()

            if user:
                user_dict = {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }
                return make_response(jsonify(user_dict), 200)
            else:
                return {'message': 'User not found'}, 404
        else:
            return {'message': '401: Not Authorized'}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()

        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id

            user_dict = {
                "id": user.id,
                "username": user.username,
                "image URL": user.image_url,
                "bio": user.bio
            }

            return make_response(
                jsonify(user_dict),
                200
            )
        
        else:
            return {"error": "Username or password is incorrect"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
    
            response = {"message": " "}

            return make_response(
                jsonify(response),
                204
            )

        else:
            response = {"error": "Unauthorized!"}
            return make_response(jsonify(response), 401)

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")

        if user_id:
            recipes = Recipe.query.all()
            recipe_data = [
                {
                    "id": r.id,
                    "title": r.title,
                    "instructions": r.instructions,
                    "minutes_to_complete": r.minutes_to_complete,
                    "user": {
                        "id": r.user.id,
                        "username": r.user.username,
                        "image_url": r.user.image_url,
                        "bio": r.user.bio
                    }
                }
                for r in recipes
            ]

            return recipe_data, 200

        return {"error": "Unauthorized. Please log in."}, 401

        
 
    def post(self):
        user_id = session.get("user_id")

        if not user_id:
            return {"error": "Unauthorized. Please log in."}, 401

        data = request.get_json()

        title = data.get("title")
        instructions = data.get("instructions")
        minutes_to_complete = data.get("minutes_to_complete")

        errors = {}
        if not title:
            errors["title"] = "Title is required."
        if not instructions:
            errors["instructions"] = "Instructions are required."
        elif len(instructions) < 50:
            errors["instructions"] = "Instructions must be at least 50 characters."
        if minutes_to_complete is None:
            errors["minutes_to_complete"] = "Minutes to complete is required."

        if errors:
            return {"errors": errors}, 422

        try:
            new_recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id
            )

            db.session.add(new_recipe)
            db.session.commit()

            from models import User  # if not already imported
            user = User.query.get(user_id)

            if not user:
                return {"error": "User not found."}, 404

            return {
                "title": new_recipe.title,
                "instructions": new_recipe.instructions,
                "minutes_to_complete": new_recipe.minutes_to_complete,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {"error": "Invalid data. Could not create recipe."}, 422


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)