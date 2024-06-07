from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from config import Config
from utils import register_error_handlers
from routes import api_bp

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
ma = Marshmallow(app)

app.register_blueprint(api_bp)

# Swagger setup
@app.route("/api/docs")
def swagger_ui():
    return render_template('swaggerui.html')

# Error handlers
register_error_handlers(app)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
