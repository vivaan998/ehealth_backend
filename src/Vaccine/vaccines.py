from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Vaccine
from serializer import VaccineSchema
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException
from src.excecptions.pagination import pagination

VACCINE_SCHEMA = VaccineSchema()


class VaccinesAPI(Resource):

    @jwt_required
    def get(self):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] != 100:
                raise UnAuthorizedException('You are not authorized')

            vaccine = Vaccine.get_all(page, search)
            if vaccine:
                prev_page, next_page = pagination('vaccines', vaccine, search)
                return make_response(jsonify({
                    "previous_page": prev_page,
                    "next_page": next_page,
                    "result": VACCINE_SCHEMA.dump(vaccine.items, many=True)
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

            result = VACCINE_SCHEMA.load(data=data)
            vaccine = Vaccine(result)
            vaccine.save()
            return make_response(jsonify({'message': 'Vaccine added successfully'}), 201)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except ValidationError as e:
            raise BadRequestException('Request data in not proper format.')
        except Exception as e:
            raise ServerException('There is some error, please contact support')
