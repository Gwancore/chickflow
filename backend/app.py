from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from models import db
from config import config
from routes import api
from reports_routes import reports
from auth_routes import auth
import os

def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Load config
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    
    # Configure CORS for production - allow all Vercel deployments
    CORS(app, 
         resources={r"/*": {"origins": "*"}},
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         supports_credentials=False)
    
    
    JWTManager(app)
    Migrate(app, db)
    
    # Register blueprints
    app.register_blueprint(auth, url_prefix='/api/auth')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(reports, url_prefix='/api/reports')
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'service': 'ChickFlow API'}), 200
    
    # Database initialization endpoint (for first-time setup)
    @app.route('/init-db')
    def init_db():
        try:
            from models import User
            from werkzeug.security import generate_password_hash
            
            # Create all tables
            db.create_all()
            
            # Check if admin user already exists
            existing_admin = User.query.filter_by(username='admin').first()
            
            if not existing_admin:
                # Create admin user
                admin = User(
                    username='admin',
                    email='admin@chickflow.com',
                    role='Admin'
                )
                admin.password_hash = generate_password_hash('admin123')
                db.session.add(admin)
                db.session.commit()
                return jsonify({
                    'status': 'success',
                    'message': 'Database initialized with admin user',
                    'credentials': {'username': 'admin', 'password': 'admin123'}
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'Database already initialized'
                }), 200
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
