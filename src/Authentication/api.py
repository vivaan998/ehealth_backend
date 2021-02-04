from flask import Blueprint
from .authenticate import LoginAPI, MenuAPI

auth_blueprint = Blueprint('auth', __name__)

login_view = LoginAPI.as_view('login_api')
menu_view = MenuAPI.as_view('test_api')

auth_blueprint.add_url_rule('/login', view_func=login_view, methods=['POST'])
auth_blueprint.add_url_rule('/menu', view_func=menu_view, methods=['GET'])
