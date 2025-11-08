"""Database initialization script for production deployment"""
from app import create_app, db
from models import User
from werkzeug.security import generate_password_hash
import os

def init_database():
    """Initialize database with tables and admin user"""
    app = create_app('production')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created")
        
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
            print("✅ Admin user created (username: admin, password: admin123)")
        else:
            print("ℹ️  Admin user already exists")
        
        print("✅ Database initialization complete!")

if __name__ == '__main__':
    init_database()
