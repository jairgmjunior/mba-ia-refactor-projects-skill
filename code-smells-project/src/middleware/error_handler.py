from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_error(error):
        return jsonify({'erro': str(error)}), 500
