from flask import Flask, make_response, jsonify
from src.excecptions.app_exception import AppException
from config import db, POSTGRES_DB_URL
from flask_jwt_extended import JWTManager
from src.Provider.providers import ProvidersAPI
from src.Practitioner.practitioners import PractitionersAPI
from src.Patient.patients import PatientsAPI
from src.Vaccine.vaccines import VaccinesAPI
from src.Authentication.authenticate import LoginAPI
from src.Common.common import MenuAPI, GetPatientsAPI, GetPractitionersAPI, GetProvidersAPI, GetVaccinesAPI, \
    SuperuserPatientsAPI, SuperuserPractitionersAPI, PractitionerAppointmentAPI, PractitionerImmunizationAPI, \
    PatientImmunizationsAPI, PatientAppointmentsAPI, VaccineAdministrationAPI, ProviderAppointmentsAPI, PatientDetailAPI
from src.Immunization.immunizations import ImmunizationAPI
from src.Appointment.appointments import AppointmentsAPI
from src.Dashboard.dashboard import ProviderImmunizationChart, MonthlyImmunizationChart, WeeklyAppointmentChart
from src.Vital.vitals import VitalsAPI
from flask_restful import Api
from flask_cors import CORS


# 'postgresql://vivek:vivek@localhost:5432/eHealth'

def create_app():
    flask_app = Flask(__name__)
    flask_app.config['DEBUG'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_DB_URL
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    flask_app.config['JWT_SECRET_KEY'] = 't1NP63m4wnBg6nyHYKfmc2TpCOGI4nss'
    db.init_app(flask_app)

    return flask_app


if __name__ == '__main__':
    app = create_app()
    jwt = JWTManager(app)
    api = Api(app)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'

    api.add_resource(LoginAPI, '/api/v1/auth/login', endpoint='login')
    api.add_resource(MenuAPI, '/api/v1/auth/menu', endpoint='menu')
    api.add_resource(ProvidersAPI, '/api/v1/providers/', endpoint='providers')
    api.add_resource(PractitionersAPI, '/api/v1/practitioners/', endpoint='practitioners')
    api.add_resource(PatientsAPI, '/api/v1/patients/', endpoint='patients')
    api.add_resource(VaccinesAPI, '/api/v1/vaccines/', endpoint='vaccines')
    api.add_resource(GetProvidersAPI, '/api/v1/get-providers/')
    api.add_resource(GetPractitionersAPI, '/api/v1/get-practitioners/<provider_id>')
    api.add_resource(GetPatientsAPI, '/api/v1/get-patients/<practitioner_id>')
    api.add_resource(GetVaccinesAPI, '/api/v1/get-vaccines/')
    api.add_resource(SuperuserPractitionersAPI, '/api/v1/super-user-practitioner/<provider_id>')
    api.add_resource(SuperuserPatientsAPI, '/api/v1/super-user-patients/<practitioner_id>')
    api.add_resource(ImmunizationAPI, '/api/v1/immunizations/', endpoint='immunizations')
    api.add_resource(AppointmentsAPI, '/api/v1/appointments/', endpoint='appointments')
    api.add_resource(VitalsAPI, '/api/v1/vitals/', endpoint='vitals')
    api.add_resource(PractitionerAppointmentAPI, '/api/v1/get-appointments-practitioner/<practitioner_id>')
    api.add_resource(PractitionerImmunizationAPI, '/api/v1/get-immunizations-practitioner/<practitioner_id>')
    api.add_resource(PatientAppointmentsAPI, '/api/v1/get-appointments-patient/<patient_id>')
    api.add_resource(PatientImmunizationsAPI, '/api/v1/get-immunizations-patient/<patient_id>')
    api.add_resource(VaccineAdministrationAPI, '/api/v1/vaccine-administered-to/<vaccine_id>')
    api.add_resource(ProviderAppointmentsAPI, '/api/v1/get-appointments-provider/<provider_id>')
    api.add_resource(PatientDetailAPI, '/api/v1/get-patient-detail/<patient_id>')
    api.add_resource(ProviderImmunizationChart, '/api/v1/provider-immunizations/')
    api.add_resource(MonthlyImmunizationChart, '/api/v1/monthly-immunizations/')
    api.add_resource(WeeklyAppointmentChart, '/api/v1/weekly-appointments/')

    @app.errorhandler(AppException)
    def app_error(err):
        app.logger.exception(err)
        return make_response(jsonify({'error': err.error}), err.http_code)


    @app.errorhandler(Exception)
    def handle_generic_error(err):
        app.logger.exception(err)
        return make_response(jsonify({'error': 'There is some issue, please contact support'}), 500)


    @jwt.invalid_token_loader
    def missing_JWT_token(msg):
        return make_response(jsonify({'error': 'Invalid token'}), 400)


    app.run(host='0.0.0.0', port='5000')

