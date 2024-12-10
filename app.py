import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Setup logging - and test git change detection
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
csrf = CSRFProtect()
app = Flask(__name__)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

login_manager.init_app(app)
login_manager.login_view = 'admin_custom.login'
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
csrf.init_app(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///events.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
db.init_app(app)
migrate = Migrate(app, db)

def setup_upload_directories():
    logger.info("Setting up upload directories...")
    
    # Ensure static folder exists
    logger.info(f"Checking static folder: {app.static_folder}")
    if not os.path.exists(app.static_folder):
        logger.info("Creating static folder...")
        os.makedirs(app.static_folder, mode=0o755)
    
    # Create uploads directory structure
    upload_base = os.path.join(app.static_folder, 'uploads')
    logger.info(f"Setting up upload base directory: {upload_base}")
    
    for directory in ['images', 'videos']:
        path = os.path.join(upload_base, directory)
        logger.info(f"Processing directory: {path}")
        
        if not os.path.exists(path):
            logger.info(f"Creating directory: {path}")
            os.makedirs(path, mode=0o755)
        else:
            logger.info(f"Directory exists: {path}")
            # Ensure correct permissions
            current_mode = os.stat(path).st_mode & 0o777
            logger.info(f"Current permissions: {oct(current_mode)}")
            os.chmod(path, 0o755)
            logger.info("Updated permissions to 755")
            
            # Set permissions for existing files
            logger.info("Checking existing files...")
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    current_mode = os.stat(file_path).st_mode & 0o777
                    logger.info(f"File {file}: current permissions {oct(current_mode)}")
                    os.chmod(file_path, 0o644)
                    logger.info(f"Updated {file} permissions to 644")
                    
    # Create images directory for placeholder if it doesn't exist
    placeholder_path = os.path.join(app.static_folder, 'images')
    logger.info(f"Checking placeholder directory: {placeholder_path}")
    if not os.path.exists(placeholder_path):
        logger.info("Creating placeholder directory...")
        os.makedirs(placeholder_path, mode=0o755)

with app.app_context():
    import models
    import routes
    import admin_views  # Import new admin views
    from admin_routes import admin_bp  # Import admin blueprint
    app.register_blueprint(admin_bp)  # Register the admin blueprint
    db.create_all()
    setup_upload_directories()
    
    # Admin user will be created after migrations are complete
    logger.info("Database initialization complete")
