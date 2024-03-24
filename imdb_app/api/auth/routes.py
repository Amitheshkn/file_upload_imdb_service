from flask import Blueprint
from flask import request
from imdb_app.api.auth.actions import UserActions

auth_app = Blueprint("auth", __name__, template_folder="templates")


@auth_app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    actions = UserActions()
    return actions.register(data)


@auth_app.route('/authenticate', methods=['POST'])
def login():
    data = request.get_json()
    actions = UserActions()
    return actions.authenticate(data)
