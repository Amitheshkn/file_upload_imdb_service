import datetime
from typing import Any

from flask import jsonify
from flask import Response
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from common.authorization import AuthorizationToken
from imdb_app.api.auth.collection_structures import USER
from imdb_app.common.definitions import Collection
from imdb_app.db.mongo_adapters import MongoAdapter


class UserActions:

    def register(self,
                 user_data):
        try:
            users_adapter = MongoAdapter(Collection.USERS)
            user_exists = users_adapter.find_document({
                USER.EMAIL: user_data[USER.EMAIL]
            })
            if user_exists:
                return jsonify({
                    "error": "User with email already exists"
                }), 400

            now = datetime.datetime.utcnow()
            users_adapter.insert_document({
                USER.EMAIL: user_data[USER.EMAIL],
                USER.CREATED_AT: now,
                USER.UPDATED_AT: now,
                USER.PASSWORD: generate_password_hash(user_data[USER.PASSWORD])
            })
            return jsonify({
                "message": "User registered successfully"
            }), 201

        except Exception as e:
            return jsonify({"error": str(e)}), 400

    def authenticate(self,
                     user_data: dict[str: Any]) -> tuple[Response, int]:
        users_adapter = MongoAdapter(Collection.USERS)
        user_details = users_adapter.find_document({
            USER.EMAIL: user_data[USER.EMAIL]
        })

        if user_details and check_password_hash(user_details[USER.PASSWORD], user_data[USER.PASSWORD]):
            user_details = {
                "user_id": str(user_details[USER.ID]),
                "email": user_details[USER.EMAIL]
            }
            token = AuthorizationToken().generate_token(user_details)
            now = datetime.datetime.utcnow()
            return jsonify({
                "user": user_details,
                "token": {
                    "key": token,
                    "issued_at": now,
                    "expires_at": now + datetime.timedelta(minutes=60)
                }
            }), 200

        else:
            return jsonify({
                "error": "User not found"
            }), 400
