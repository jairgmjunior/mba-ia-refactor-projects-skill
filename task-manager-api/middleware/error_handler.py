from flask import jsonify
from database import db

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_error(error):
        db.session.rollback()
        return jsonify({'error': str(error)}), 500
