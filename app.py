import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_migrate import Migrate

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
app = Flask(__name__)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

login_manager.init_app(app)
login_manager.login_view = 'admin.login'
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///events.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)
migrate = Migrate(app, db)

def setup_upload_directories():
    # Ensure static folder exists
    if not os.path.exists(app.static_folder):
        os.makedirs(app.static_folder, mode=0o755)
    
    # Create uploads directory structure
    upload_base = os.path.join(app.static_folder, 'uploads')
    for directory in ['images', 'videos']:
        path = os.path.join(upload_base, directory)
        if not os.path.exists(path):
            os.makedirs(path, mode=0o755)
        else:
            # Ensure correct permissions
            os.chmod(path, 0o755)
            # Set permissions for existing files
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    os.chmod(file_path, 0o644)
                    
    # Create images directory for placeholder if it doesn't exist
    placeholder_path = os.path.join(app.static_folder, 'images')
    if not os.path.exists(placeholder_path):
        os.makedirs(placeholder_path, mode=0o755)

with app.app_context():
    import models
    import routes
    import admin_views  # Import new admin views
    from admin_routes import admin_bp  # Import admin blueprint
    app.register_blueprint(admin_bp)  # Register the admin blueprint
    db.create_all()
    setup_upload_directories()
    
    # Create admin user if it doesn't exist
    from models import User
    logger.info("Checking for admin user existence...")
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        logger.info("Creating admin user...")
        admin_user = User(username='admin', email='admin@example.com', is_admin=True)
        admin_user.set_password('admin')  # Default password, should be changed
        db.session.add(admin_user)
        db.session.commit()
        logger.info("Admin user created successfully with admin privileges enabled")
    else:
        logger.info("Admin user already exists")
