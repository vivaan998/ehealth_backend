from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import make_response, jsonify
from model import Users, RolePermission, Provider, Practitioner, Patient
from src.excecptions.app_exception import ServerException
from serializer import ProviderSchema, PractitionerSchema, PatientSchema

PROVIDERS_SCHEMA = ProviderSchema()
PRACTITIONERS_SCHEMA = PractitionerSchema()
PATIENTS_SCHEMA = PatientSchema()


class MenuAPI(Resource):

    @jwt_required
    def get(self):
        try:
            user = get_jwt_identity()
            menu = RolePermission.get_permissions(user['role'])
            name, designation = Users.get_name(user['role'], user['email'])
            return make_response(jsonify({'menu': menu, 'data': {'name': name, 'designation': designation,
                                                                 'role': user['role']}}), 200)
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
                return make_response(jsonify([]), 200)

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
                return make_response(jsonify([]), 200)

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
                return make_response(jsonify([]), 200)

        except Exception as e:
            raise ServerException('There is some error, please contact support')