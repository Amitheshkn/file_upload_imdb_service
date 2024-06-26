import datetime
import functools
from typing import Callable
from typing import Optional

import jwt
from flask import jsonify
from flask import request

from imdb_app.core.config import CONF


class AuthorizationToken:
    SECRET_KEY = CONF.application.secret_key

    def verify_token(self,
                     token: str,
                     /,
                     *,
                     decoded: bool = False) -> Optional[dict]:
        result = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
        if decoded:
            return result

    def generate_token(self,
                       user_details: dict[str: str]) -> str:
        """
        Generates a JWT token with an expiration time.
        :return: A JWT token as a string.
        """
        now = datetime.datetime.utcnow()
        payload = {
            "exp": now + datetime.timedelta(hours=1),  # Expiration time
            "iat": now,
            "ui": user_details["user_id"],
            "ue": user_details["email"]
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
        return token


def check_authentication(f) -> Callable:
    """Decorator for REST API Authentication"""

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for the authorization header
        try:
            token = request.headers.get("Auth-Token")
            if token:
                AuthorizationToken().verify_token(token)
            else:
                return jsonify({
                    "message": "Token is missing!"
                }), 403
        except BaseException:
            return jsonify({
                "message": "Invalid token"
            }), 401

        return f(*args, **kwargs)

    return decorated_function


def get_user_ctx_from_token(request_: request) -> dict[str, str]:
    token = request_.headers.get('Auth-Token')
    decoded = AuthorizationToken().verify_token(token, decoded=True)
    user_context = {
        "user_id": decoded.get("ui"),
        "user_email": decoded.get("ue")
    }
    return user_context
