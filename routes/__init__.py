from flask import Blueprint

from .auth import auth_bp
from .books import books_bp
from .reviews import reviews_bp

# Create a Blueprint for the API
api_bp = Blueprint('api', __name__)

# Register blueprints
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(books_bp, url_prefix='/books')
api_bp.register_blueprint(reviews_bp, url_prefix='/reviews')
