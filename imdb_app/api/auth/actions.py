import datetime
from typing import Any, Tuple

from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, Response

from common.authorization import AuthorizationToken
from imdb_app import utils
from imdb_app.db.mongo_adapters import MongoAdapter


class UserActions:

    def register(self,
                 user_data):
        try:
            users_adapter = MongoAdapter("users")
            user_exists = users_adapter.find_one({
                "email": user_data["email"]
            })
            if user_exists:
                return jsonify({
                    "error": "User with email already exists"
                }), 400

            users_adapter.insert_one({
                "email": user_data["email"],
                "password": generate_password_hash(user_data['password'])
            })
            return jsonify({
                "message": "User registered successfully"
            }), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def authenticate(self,
                     user_data: dict[str: Any]) -> tuple[Response, int]:
        users_adapter = MongoAdapter("users")
        user_details = users_adapter.find_one({
            "email": user_data["email"]
        })

        if user_details and check_password_hash(user_details["password"], user_data["password"]):
            token = AuthorizationToken().generate_token(str(user_details["_id"]), user_details["email"])
            now = datetime.datetime.utcnow()
            return jsonify({
                "user": {
                    "user_id": str(user_details["_id"]),
                    "email": user_details["email"]
                },
                "token": {
                    "key": token,
                    "issued_at": now,
                    "expires_at": now + datetime.timedelta(minutes=60)
                }
            }), 201
        
        else:
            jsonify({
                "error": "User not found"
            }), 400
