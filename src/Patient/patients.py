from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Users, Practitioner, Patient, Provider
from serializer import PatientSchema, UsersSchema
from config import PATIENT
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException

PATIENTS_SCHEMA = PatientSchema()
USER_SCHEMA = UsersSchema()


class PatientsAPI(Resource):

    @jwt_required
    def get(self):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] == 100:
                patients = Patient.get_all(page, search)
            elif user['role'] == 50:
                provider_id = Provider.get_by_email(user['email'])[0].provider_id
                patients = Patient.get_patient_by_providers(page, search, provider_id)
            elif user['role'] == 10:
                practitioner_id = Practitioner.get_by_email(user['email'])[0].practitioner_id
                patients = Patient.get_patient_by_practitioners(page, search, practitioner_id)
            else:
                raise UnAuthorizedException('You are not authorized')

            if patients:
                return make_response(jsonify({
                    "previous_page": patients.prev_num,
                    "next_page": patients.next_num,
                    "result": PATIENTS_SCHEMA.dump(patients.items, many=True)
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

            if user['role'] == 100 or user['role'] == 50 or user['role'] == 10:
                if not data.get('provider_id') and not data.get('practitioner_id'):
                    practitioner = Practitioner.get_by_email(user['email'])[0]
                    data["provider_id"] = practitioner.provider_id
                    data['practitioner_id'] = practitioner.practitioner_id
                elif not data.get('provider_id'):
                    data["provider_id"] = Provider.get_by_email(user['email'])[0].provider_id
            else:
                raise UnAuthorizedException('You are not authorized')

            user_data = {
                "user_email": data.get('email_tx'),
                "hash_password": data.get('password'),
                "security_role": PATIENT
            }

            data.pop('password')
            result = PATIENTS_SCHEMA.load(data=data)
            patient = Patient(result)
            user_result = USER_SCHEMA.load(data=user_data)
            users = Users(user_result)
            users.save()
            patient.save()
            return make_response(jsonify({'message': 'Patient created successfully'}), 201)

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

            patient = Patient.get_one(data['patient_id'])

            if patient:
                patient.update()
                return make_response(jsonify({'message': 'Patient archived successfully'}), 202)
            else:
                raise BadRequestException('No such patient found')

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
