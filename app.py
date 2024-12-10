import os
import logging
from flask import Flask
from extensions import db, login_manager, csrf, migrate, ckeditor

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///events.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_custom.login'
    csrf.init_app(app)
    migrate.init_app(app, db)
    ckeditor.init_app(app)
    
    # Register theme context processor after database initialization
    with app.app_context():
        try:
            from utils.theme_manager import inject_theme, initialize_default_themes
            app.context_processor(inject_theme)
            initialize_default_themes()  # Initialize themes right after context processor
            app.logger.info("Theme system initialized successfully")
        except Exception as e:
            app.logger.error(f"Error initializing theme system: {str(e)}")
    
    return app

app = create_app()

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

def register_extensions(app):
    """Register Flask extensions and blueprints."""
    try:
        # Create database tables first
        with app.app_context():
            import models  # This import creates the models
            db.create_all()
            logger.info("Database tables created successfully")
            
            # Initialize default themes
            from utils.theme_manager import initialize_default_themes
            initialize_default_themes()
            logger.info("Theme initialization completed")
        
        # Import views and routes here to avoid circular imports
        from admin_routes import admin_bp
        
        # Register admin blueprint first
        app.register_blueprint(admin_bp)
        
        # Import and initialize admin views after blueprint registration
        import admin_views
        admin = admin_views.init_admin(app)
        
        # Import routes last to avoid circular dependencies
        import routes
        
        logger.info("All extensions and blueprints registered successfully")
        return app
    except Exception as e:
        app.logger.error(f"Error registering extensions: {str(e)}")
        raise

with app.app_context():
    try:
        import models  # This import creates the models
        db.create_all()
        logger.info("Database tables created successfully")
        
        setup_upload_directories()
        logger.info("Upload directories configured")
        
        register_extensions(app)
        logger.info("Extensions registered")
        
        # Initialize default themes
        from utils.theme_manager import initialize_default_themes
        initialize_default_themes()
        logger.info("Theme initialization completed")
        
        logger.info("Application initialization complete")
    except Exception as e:
        logger.error(f"Error during application initialization: {str(e)}")
        raise
