"""
Main Flask application entry point.

This module sets up the Flask server, registers all routes, and configures CORS.
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import config

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.group_routes import group_bp
from routes.contribution_routes import contribution_bp
from routes.loan_routes import loan_bp


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = config.SECRET_KEY
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(group_bp, url_prefix='/api/groups')
    app.register_blueprint(contribution_bp, url_prefix='/api/contributions')
    app.register_blueprint(loan_bp, url_prefix='/api/loans')
    
    # Serve frontend
    @app.route('/')
    def index():
        return send_from_directory('templates', 'index.html')
    
    @app.route('/<path:path>')
    def serve_static(path):
        return send_from_directory('static', path)
    
    return app


if __name__ == '__main__':
    app = create_app()
    print(f"""
╔════════════════════════════════════════════════════════════╗
║   Savings & Loan Application Server                       ║
║   Server running on http://{config.HOST}:{config.PORT}           ║
║   Press Ctrl+C to quit                                     ║
╚════════════════════════════════════════════════════════════╝
    """)
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
