import datetime
from flask_restful import Resource
from flask_jwt_extended import create_access_token, create_refresh_token
from flask import make_response, request, jsonify
from model import Users
from src.excecptions.app_exception import BadRequestException, ServerException


class LoginAPI(Resource):

    @staticmethod
    def post():
        try:
            data = request.get_json()
            user = Users.get_user(user_email=data.get('email'))
            if not user:
                raise BadRequestException('Not authorized to login')

            authorized = user.check_password(data.get('password'))
            if not authorized:
                raise BadRequestException('Invalid credentials')

            user_claims = {
                "id": user.user_id,
                "email": user.user_email,
                "role": user.security_role
            }
            expires = datetime.timedelta(days=7)
            access_token = create_access_token(identity=user_claims, expires_delta=expires)
            refresh_token = create_refresh_token(identity=user_claims)

            return make_response(jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200)

        except BadRequestException as e:
            raise BadRequestException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
