import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta

from database import init_db, close_db
from routes import api

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET", "studyq-secret-key-change-in-prod")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

CORS(app, resources={r"/api/*": {"origins": "*"}})
jwt = JWTManager(app)

app.teardown_appcontext(close_db)

# Register routes blueprint under /api
app.register_blueprint(api, url_prefix='/api')

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
