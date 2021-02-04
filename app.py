from flask import Flask, make_response, jsonify
from src.excecptions.app_exception import AppException
from config import db
from flask_jwt_extended import JWTManager
from src.Authentication.api import auth_blueprint


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    import model
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:attache123@attache-dev-db1.c00qcl0ls8g4.us-east-1.rds.amazonaws.com:5432/eHealth'
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 't1NP63m4wnBg6nyHYKfmc2TpCOGI4nss'

    return app


if __name__ == '__main__':
    app = create_app()
    jwt = JWTManager(app)

    app.register_blueprint(auth_blueprint, url_prefix='/api/v1/auth')


    @app.errorhandler(AppException)
    def app_error(err):
        app.logger.exception(err)
        return make_response(jsonify(err.error), err.http_code)


    @app.errorhandler(Exception)
    def handle_generic_error(err):
        app.logger.exception(err)
        return make_response(jsonify({'error': err}), 500)

    @jwt.invalid_token_loader
    def missing_JWT_token(msg):
        return make_response(jsonify({'error': 'Invalid token'}), 400)

    app.run(host='127.0.0.1', port='5000')
