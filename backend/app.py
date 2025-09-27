# app.py
from flask import Flask
from flask_cors import CORS
from models import Base
from database import engine
from routes.events import events_bp
from routes.payment import payment_bp
from routes.admin import admin_bp
import os

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "superpicklesecret")  # required for sessions
    CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}
)# If you want to be stricter later, replace "*" with http://localhost:5173.

    # Register admin routes
    #app.register_blueprint(admin_bp)


    # Initialize DB schema (creates tables if not exist)
    Base.metadata.create_all(bind=engine)

    # Register blueprints
    app.register_blueprint(events_bp, url_prefix="/api/events")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    for rule in app.url_map.iter_rules():
        print(rule)


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
