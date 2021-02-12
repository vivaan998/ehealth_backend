from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Provider, Practitioner, Patient, Vitals
from serializer import VitalSchema
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException

VITAL_SCHEMA = VitalSchema()


class VitalsAPI(Resource):

    @jwt_required
    def get(self):
        try:
            page = request.args.get('page', 1)
            patient_id = request.args.get('patient_id', None)
            if not patient_id:
                raise BadRequestException('Patient ID missing, please check url')

            vitals, next_num, prev_num = Vitals.get_vital_by_patients(page, patient_id=patient_id)

            if vitals:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": vitals
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except BadRequestException as e:
            raise BadRequestException(e.error)
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

            result = VITAL_SCHEMA.load(data=data)
            vital = Vitals(result)
            vital.save()
            return make_response(jsonify({'message': 'Vital added successfully'}), 201)

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

            vital = Vitals.get_one(data['vital_id'])

            if vital:
                vital.update()
                return make_response(jsonify({'message': 'Vital archived successfully'}), 202)
            else:
                raise BadRequestException('No such Vital found')

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
