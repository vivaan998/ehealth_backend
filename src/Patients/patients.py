import datetime
from flask.views import MethodView
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from flask import make_response, request, jsonify
from model import Users, RolePermission, Permissions


class LoginAPI(MethodView):

    @staticmethod
    def post():
        data = request.get_json()
        user = Users.get_user(user_email=data.get('email'))
        authorized = user.check_password(data.get('password'))
        if not authorized:
            return make_response(jsonify({'error': 'Email or password invalid'}), 401)

        user_claims = {
            "id": user.user_id,
            "email": user.user_email,
            "role": user.security_role
        }
        expires = datetime.timedelta(days=7)
        access_token = create_access_token(identity=user_claims, expires_delta=expires)
        refresh_token = create_refresh_token(identity=user_claims)

        return make_response(jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200)


class MenuAPI(MethodView):

    @staticmethod
    @jwt_required
    def get():
        user = get_jwt_identity()
        permissions = RolePermission.get_permissions(user['role'])
        menu_list = Permissions.get_permissions(permissions)
        return make_response(jsonify({'data': menu_list}), 200)



