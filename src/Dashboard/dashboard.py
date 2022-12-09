from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, jsonify
from model import Appointment, Immunization
from src.excecptions.app_exception import ServerException, UnAuthorizedException


class ProviderImmunizationChart(Resource):

    @jwt_required
    def get(self):
        try:
            user = get_jwt_identity()
            if user['role'] != 100:
                UnAuthorizedException('You are not authorized')

            immunization_providers = Immunization.provider_immunization_chart()
            return make_response(jsonify({'result': immunization_providers,
                                          'count': len(immunization_providers)}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class MonthlyImmunizationChart(Resource):

    @jwt_required
    def get(self):
        try:
            user = get_jwt_identity()
            if user['role'] != 100:
                UnAuthorizedException('You are not authorized')

            monthly_immunizations = Immunization.monthly_immunization_chart()
            return make_response(jsonify({'result': monthly_immunizations}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class WeeklyAppointmentChart(Resource):

    @jwt_required
    def get(self):
        try:
            user = get_jwt_identity()
            if user['role'] != 100:
                UnAuthorizedException('You are not authorized')

            weekly_appointments = Appointment.appointments_chart()
            return make_response(jsonify({'result': weekly_appointments}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
