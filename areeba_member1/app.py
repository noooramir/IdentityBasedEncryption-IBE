from __future__ import annotations
import os
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from config import Config
from database import close_db, init_db
from routes.auth_routes import auth_bp
from routes.ibe_routes import ibe_bp
from request_security import validate_request_timestamp
from api_response import error_response, success_response

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    app.register_blueprint(auth_bp)
    app.register_blueprint(ibe_bp)
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()

    @app.before_request
    def enforce_request_timestamp():
        if request.method == "OPTIONS":
            return None
        if request.path == "/" or request.path == "/favicon.ico":
            return None
        raw_timestamp = request.headers.get("X-Request-Timestamp")
        error_message = validate_request_timestamp(raw_timestamp)
        if error_message is not None:
            return error_response(error_message)

    @app.errorhandler(400)
    def bad_request(_error):
        return error_response("Bad request.")

    @app.errorhandler(404)
    def not_found(_error):
        return error_response("Resource not found.", 404)

    @app.errorhandler(405)
    def method_not_allowed(_error):
        return error_response("Method not allowed.", 405)

    @app.errorhandler(500)
    def internal_server_error(_error):
        return error_response("Internal server error.", 500)

    @app.get("/")
    def serve_frontend():
        return send_from_directory(os.path.dirname(__file__), "index.html")

    return app

app = create_app()
if __name__ == "__main__":
    app.run(debug=True)