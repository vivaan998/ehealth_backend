from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Users, Provider
from serializer import ProviderSchema, UsersSchema
from config import PROVIDER
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException

PROVIDERS_SCHEMA = ProviderSchema()
USER_SCHEMA = UsersSchema()


class ProvidersAPI(Resource):

    @jwt_required
    def get(self):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] != 100:
                raise UnAuthorizedException('You are not authorized')

            providers = Provider.get_all(page, search)
            if providers:
                return make_response(jsonify({
                    "previous_page": providers.prev_num,
                    "next_page": providers.next_num,
                    "result": PROVIDERS_SCHEMA.dump(providers.items, many=True)
                }), 200)
            else:
                return make_response(jsonify([]), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')

    @jwt_required
    def post(self):
        try:
            user = get_jwt_identity()
            data = request.get_json()
            if user['role'] != 100:
                raise UnAuthorizedException('You are not authorized')

            if Users.get_user(user_email=data.get('email')):
                raise BadRequestException(data.get('email') + ' already exists, please login')

            provider_data = {
                "site_admin_email": data.get('email'),
                "name_tx": data.get('name')
            }

            user_data = {
                "user_email": data.get('email'),
                "hash_password": data.get('password'),
                "security_role": PROVIDER
            }

            result = PROVIDERS_SCHEMA.load(data=provider_data)
            provider = Provider(result)
            user_result = USER_SCHEMA.load(data=user_data)
            users = Users(user_result)
            users.save()
            provider.save()
            return make_response(jsonify({'message': 'Provider created successfully'}), 201)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except ValidationError as e:
            raise BadRequestException('Request data in not proper format.')
        except Exception as e:
            raise ServerException('There is some error, please contact support')
