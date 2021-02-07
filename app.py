from flask import Flask, make_response, jsonify
from src.excecptions.app_exception import AppException
from config import db, POSTGRES_DB_URL
from flask_jwt_extended import JWTManager
from src.Provider.providers import ProvidersAPI
from src.Practitioner.practitioners import PractitionersAPI
from src.Authentication.authenticate import MenuAPI, LoginAPI
from flask_restful import Api
from flask_cors import CORS, cross_origin


# 'postgresql://vivek:vivek@localhost:5432/eHealth'

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_DB_URL
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 't1NP63m4wnBg6nyHYKfmc2TpCOGI4nss'

    return app


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
