import math
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, jsonify, request
from model import Users, RolePermission, Provider, Practitioner, Patient, Vaccine, Appointment, Immunization, PER_PAGE
from src.excecptions.app_exception import ServerException, UnAuthorizedException
from serializer import PractitionerSchema, PatientSchema

PRACTITIONERS_SCHEMA = PractitionerSchema()
PATIENTS_SCHEMA = PatientSchema()


class MenuAPI(Resource):

    @jwt_required
    def get(self):
        try:
            user = get_jwt_identity()
            menu = RolePermission.get_permissions(user['role'])
            name, designation, user_id, practitioner_name, provider_name = Users.get_name(user['role'], user['email'])
            return make_response(jsonify({'menu': menu, 'data': {'name': name, 'designation': designation,
                                                                 'role': user['role'], 'id': user_id,
                                                                 'practitioner': practitioner_name, 'provider':
                                                                     provider_name}}), 200)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class PatientDetailAPI(Resource):

    @jwt_required
    def get(self, patient_id):
        try:
            patient = Patient.get_one(patient_id)
            name = patient.first_name + " " + patient.last_name
            return make_response(jsonify({'patient_id': patient.patient_id, 'patient_name': name,
                                          'patient_email': patient.email_tx}), 200)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class GetProvidersAPI(Resource):

    @jwt_required
    def get(self):
        try:
            providers = Provider.get()
            result = []
            if providers:
                for provider in providers:
                    result.append({
                        "name": provider.name_tx,
                        "provider_id": provider.provider_id
                    })
                return make_response(jsonify({'data': result}), 200)
            else:
                return make_response(jsonify({"data": []}), 200)

        except Exception as e:
            raise ServerException('There is some error, please contact support')


class GetPractitionersAPI(Resource):

    @jwt_required
    def get(self, provider_id):
        try:
            practitioners = Practitioner.get(provider_id)
            result = []
            if practitioners:
                for practitioner in practitioners:
                    result.append({
                        "name": practitioner.first_name + " " + practitioner.last_name,
                        "practitioner_id": practitioner.practitioner_id,
                        "provider_id": practitioner.provider_id
                    })
                return make_response(jsonify({'data': result}), 200)
            else:
                return make_response(jsonify({"data": []}), 200)

        except Exception as e:
            raise ServerException('There is some error, please contact support')


class GetPatientsAPI(Resource):

    @jwt_required
    def get(self, practitioner_id):
        try:
            patients = Patient.get(practitioner_id)
            result = []
            if patients:
                for patient in patients:
                    result.append({
                        "name": patient.first_name + " " + patient.last_name,
                        "patient_id": patient.patient_id,
                        "practitioner_id": patient.practitioner_id,
                        "provider_id": patient.provider_id
                    })
                return make_response(jsonify({'data': result}), 200)
            else:
                return make_response(jsonify({"data": []}), 200)

        except Exception as e:
            raise ServerException('There is some error, please contact support')


class GetVaccinesAPI(Resource):

    @jwt_required
    def get(self):
        try:
            vaccines = Vaccine.get()
            result = []
            if vaccines:
                for vaccine in vaccines:
                    result.append({
                        "name": vaccine.name_tx,
                        "vaccine_id": vaccine.vaccine_id,
                    })
                return make_response(jsonify({'data': result}), 200)
            else:
                return make_response(jsonify({"data": []}), 200)

        except Exception as e:
            raise ServerException('There is some error, please contact support')


class SuperuserPractitionersAPI(Resource):

    @jwt_required
    def get(self, provider_id):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()
            if user['role'] < 50:
                raise UnAuthorizedException('You are not authorized')

            practitioners = Practitioner.get_practitioners_by_providers(page, search, provider_id)
            if practitioners:
                return make_response(jsonify({
                    "previous_page": practitioners.prev_num,
                    "next_page": practitioners.next_num,
                    "result": PRACTITIONERS_SCHEMA.dump(practitioners.items, many=True),
                    "total_count": practitioners.total,
                    "total_pages": math.ceil(practitioners.total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class SuperuserPatientsAPI(Resource):

    @jwt_required
    def get(self, practitioner_id):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] < 50:
                raise UnAuthorizedException('You are not authorized')

            patients = Patient.get_patient_by_practitioners(page, search, practitioner_id)
            if patients:
                return make_response(jsonify({
                    "previous_page": patients.prev_num,
                    "next_page": patients.next_num,
                    "result": PATIENTS_SCHEMA.dump(patients.items, many=True),
                    "total_count": patients.total,
                    "total_pages": math.ceil(patients.total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class ProviderAppointmentsAPI(Resource):

    @jwt_required
    def get(self, provider_id):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()

            if user['role'] != 100:
                raise UnAuthorizedException('You are not authorized')

            appointments, next_num, prev_num, total = Appointment.get_appointment_by_providers(page, search, provider_id)
            if appointments:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": appointments,
                    "total_count": total,
                    "total_pages": math.ceil(total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class PractitionerAppointmentAPI(Resource):

    @jwt_required
    def get(self, practitioner_id):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()
            if user['role'] < 50:
                raise UnAuthorizedException('You are not authorized')

            appointments, next_num, prev_num, total = Appointment.get_appointment_by_practitioners(page, search,
                                                                                                   practitioner_id)
            if appointments:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": appointments,
                    "total_count": total,
                    "total_pages": math.ceil(total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class PractitionerImmunizationAPI(Resource):

    @jwt_required
    def get(self, practitioner_id):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()
            if user['role'] < 50:
                raise UnAuthorizedException('You are not authorized')

            immunizations, next_num, prev_num, total = Immunization.get_immunization_by_practitioners(page, search,
                                                                                                      practitioner_id)
            if immunizations:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": immunizations,
                    "total_count": total,
                    "total_pages": math.ceil(total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class VaccineAdministrationAPI(Resource):

    @jwt_required
    def get(self, vaccine_id):
        try:
            page = request.args.get('page', 1)
            search = request.args.get('search', None)
            user = get_jwt_identity()
            if user['role'] != 100:
                raise UnAuthorizedException('You are not authorized')

            administered, next_num, prev_num, total = Immunization.get_vaccines_administered(page, search, vaccine_id)
            if administered:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": administered,
                    "total_count": total,
                    "total_pages": math.ceil(total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class PatientAppointmentsAPI(Resource):

    @jwt_required
    def get(self, patient_id):
        try:
            page = request.args.get('page', 1)
            user = get_jwt_identity()
            if user['role'] < 10:
                raise UnAuthorizedException('You are not authorized')

            appointments, next_num, prev_num, total = Appointment.get_appointment_by_patients(page, patient_id)
            if appointments:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": appointments,
                    "total_count": total,
                    "total_pages": math.ceil(total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')


class PatientImmunizationsAPI(Resource):

    @jwt_required
    def get(self, patient_id):
        try:
            page = request.args.get('page', 1)
            user = get_jwt_identity()
            if user['role'] < 10:
                raise UnAuthorizedException('You are not authorized')

            immunizations, next_num, prev_num, total = Immunization.get_immunization_by_patients(page, patient_id)
            if immunizations:
                return make_response(jsonify({
                    "previous_page": prev_num,
                    "next_page": next_num,
                    "result": immunizations,
                    "total_count": total,
                    "total_pages": math.ceil(total / PER_PAGE)
                }), 200)
            else:
                return make_response(jsonify({"result": []}), 200)

        except UnAuthorizedException as e:
            raise UnAuthorizedException(e.error)
        except Exception as e:
            raise ServerException('There is some error, please contact support')
