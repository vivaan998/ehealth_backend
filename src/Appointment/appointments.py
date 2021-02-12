from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, request, jsonify
from marshmallow import ValidationError
from model import Provider, Practitioner, Patient, Appointment
from serializer import AppointmentSchema
from src.excecptions.app_exception import BadRequestException, UnAuthorizedException, ServerException

APPOINTMENT_SCHEMA = AppointmentSchema()


class AppointmentsAPI(Resource):

    @jwt_required
    def get(self):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] == 100:
                appointments, next_num, prev_num = Appointment.get_all(page, search)

            elif user['role'] == 50:
                provider_id = Provider.get_by_email(user['email'])[0].provider_id
                appointments, next_num, prev_num = Appointment.get_appointment_by_providers(page, search, provider_id)
            elif user['role'] == 10:
                practitioner_id = Practitioner.get_by_email(user['email'])[0].practitioner_id
                appointments, next_num, prev_num = Appointment.get_appointment_by_practitioners(page, search,
                                                                                                practitioner_id)
            else:
                patient_id = Patient.get_by_email(user['email'])[0].patient_id
                appointments, next_num, prev_num = Appointment.get_appointment_by_patients(page, patient_id)

            if appointments:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": appointments
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

            result = APPOINTMENT_SCHEMA.load(data=data)
            appointment = Appointment(result)
            appointment.save()
            return make_response(jsonify({'message': 'Appointment added successfully'}), 201)

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

            appointment = Appointment.get_one(data['appointment_id'])

            if appointment:
                appointment.update()
                return make_response(jsonify({'message': 'Appointment archived successfully'}), 202)
            else:
                raise BadRequestException('No such appointment found')

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except BadRequestException as e:
            raise BadRequestException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
