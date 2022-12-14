import math

from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Vaccine, PER_PAGE
from serializer import VaccineSchema
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException

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

            vaccines = Vaccine.get_all(page, search)
            if vaccines:
                return make_response(jsonify({
                    "previous_page": vaccines.prev_num,
                    "next_page": vaccines.next_num,
                    "result": VACCINE_SCHEMA.dump(vaccines.items, many=True),
                    "total_count": vaccines.total,
                    "total_pages": math.ceil(vaccines.total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

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

    @jwt_required
    def put(self):
        try:
            user = get_jwt_identity()
            data = request.get_json()
            if user['role'] < 100:
                raise UnAuthorizedException('You are not authorized')

            vaccine = Vaccine.get_one(data['vaccine_id'])

            if vaccine:
                vaccine.update()
                return make_response(jsonify({'message': 'Vaccine archived successfully'}), 202)
            else:
                raise BadRequestException('No such vaccine found')

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
