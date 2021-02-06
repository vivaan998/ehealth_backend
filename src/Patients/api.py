from flask import Blueprint
from .patients import LoginAPI, MenuAPI

auth_blueprint = Blueprint('patients', __name__)

login_view = LoginAPI.as_view('login_api')
menu_view = MenuAPI.as_view('menu_api')

auth_blueprint.add_url_rule('/auth/login', view_func=login_view, methods=['POST'])
auth_blueprint.add_url_rule('/auth/menu', view_func=menu_view, methods=['GET'])
