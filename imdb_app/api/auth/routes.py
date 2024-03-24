from flask import Blueprint, jsonify
from flask import request

from imdb_app.api.auth.actions import UserActions

auth_app = Blueprint("auth", __name__, template_folder="templates")


@auth_app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        return jsonify({
            "error": "Email and password are required."
        }), 400

    actions = UserActions()
    return actions.register(data)


@auth_app.route("/authenticate", methods=["POST"])
def login():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        return jsonify({
            "error": "Email and password are required."
        }), 400

    actions = UserActions()
    return actions.authenticate(data)
