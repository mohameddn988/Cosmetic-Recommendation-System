from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    
    # Register blueprints
    from app.routes.scraping_routes import scraping_bp
    from app.routes.api_routes import api_bp
    
    app.register_blueprint(scraping_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app