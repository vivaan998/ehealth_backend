from flask import Flask, make_response, jsonify
from src.excecptions.app_exception import AppException
from config import db


# postgresql://vivek:vivek@localhost:5432/eHealth

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    import model
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://vivek:vivek@localhost:5432/eHealth'
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.register_blueprint(bp_authenticate, url_prefix='/api/v1/authenticate')
    return app


def setup_database(flask_app):
    with flask_app.app_context():
        db.create_all()


if __name__ == '__main__':
    app = create_app()
    setup_database(app)


    @app.errorhandler(AppException)
    def app_error(err):
        app.logger.exception(err)
        return make_response(jsonify(err.error), err.http_code)


    @app.errorhandler(Exception)
    def handle_generic_error(err):
        app.logger.exception(err)
        return make_response(jsonify(str(err)), 500)


    app.run(host='127.0.0.1', port='5000')
