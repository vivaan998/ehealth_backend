from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Provider, Practitioner, Immunization, Patient
from serializer import ImmunizationSchema
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException

IMMUNIZATION_SCHEMA = ImmunizationSchema()


class ImmunizationAPI(Resource):

    @jwt_required
    def get(self):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] == 100:
                immunization, next_num, prev_num = Immunization.get_all(page, search)

            elif user['role'] == 50:
                provider_id = Provider.get_by_email(user['email'])[0].provider_id
                immunization, next_num, prev_num = Immunization.get_immunization_by_providers(page, search, provider_id)
            elif user['role'] == 10:
                practitioner_id = Practitioner.get_by_email(user['email'])[0].practitioner_id
                immunization, next_num, prev_num = Immunization.get_immunization_by_practitioners(page, search,
                                                                                                  practitioner_id)
            else:
                patient_id = Patient.get_by_email(user['email'])[0].patient_id
                immunization, next_num, prev_num = Immunization.get_immunization_by_patients(page, patient_id)

            if immunization:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": immunization
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

            if user['role'] == 100 or user['role'] == 50 or user['role'] == 10:
                if not data.get('provider_id') and not data.get('practitioner_id'):
                    practitioner = Practitioner.get_by_email(user['email'])[0]
                    data["provider_id"] = practitioner.provider_id
                    data['practitioner_id'] = practitioner.practitioner_id
                elif not data.get('provider_id'):
                    data["provider_id"] = Provider.get_by_email(user['email'])[0].provider_id
            else:
                raise UnAuthorizedException('You are not authorized')

            result = IMMUNIZATION_SCHEMA.load(data=data)
            immunization = Immunization(result)
            immunization.save()
            return make_response(jsonify({'message': 'Immunization added successfully'}), 201)

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
            if user['role'] < 10:
                raise UnAuthorizedException('You are not authorized')

            immunization = Immunization.get_one(data['immunization_id'])

            if immunization:
                immunization.update()
                return make_response(jsonify({'message': 'Immunization archived successfully'}), 202)
            else:
                raise BadRequestException('No such immunization found')

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
