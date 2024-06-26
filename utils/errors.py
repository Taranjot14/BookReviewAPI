from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def resource_not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(error="An internal error occurred. Please try again later."), 500
