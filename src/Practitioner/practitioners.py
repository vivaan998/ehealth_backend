from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Users, Practitioner, Provider
from serializer import PractitionerSchema, UsersSchema
from config import PRACTITIONER
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException
from src.excecptions.pagination import pagination

PRACTITIONERS_SCHEMA = PractitionerSchema()
USER_SCHEMA = UsersSchema()


class PractitionersAPI(Resource):

    @jwt_required
    def get(self):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] == 100:
                practitioner = Practitioner.get_all(page, search)
            elif user['role'] == 50:
                provider_id = Provider.get_by_email(user['email'])[0].provider_id
                practitioner = Practitioner.get_practitioners_by_providers(page, search, provider_id)
            else:
                raise UnAuthorizedException('You are not authorized')

            if practitioner:
                prev_page, next_page = pagination('practitioners', practitioner, search)
                return make_response(jsonify({
                    "previous_page": prev_page,
                    "next_page": next_page,
                    "result": PRACTITIONERS_SCHEMA.dump(practitioner.items, many=True)
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

            if Users.get_user(user_email=data.get('email_tx')):
                raise BadRequestException(data.get('email_tx') + ' already exists, please login')

            if user['role'] == 100 or user['role'] == 50:
                if not data.get('provider_id'):
                    provider_id = Provider.get_by_email(user['email'])[0].provider_id
                    data["provider_id"] = provider_id
            else:
                raise UnAuthorizedException('You are not authorized')

            user_data = {
                "user_email": data.get('email_tx'),
                "hash_password": data.get('password'),
                "security_role": PRACTITIONER
            }

            data.pop('password')
            result = PRACTITIONERS_SCHEMA.load(data=data)
            practitioner = Practitioner(result)
            user_result = USER_SCHEMA.load(data=user_data)
            users = Users(user_result)
            users.save()
            practitioner.save()
            return make_response(jsonify({'message': 'Practitioner created successfully'}), 201)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except ValidationError as e:
            raise BadRequestException('Request data in not proper format.')
        except Exception as e:
            raise ServerException('There is some error, please contact support')
