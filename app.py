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
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["FLASK_ADMIN_SWATCH"] = "cosmo"
    
    try:
        # Initialize extensions
        db.init_app(app)
        login_manager.init_app(app)
        login_manager.login_view = 'admin_custom.login'
        csrf.init_app(app)
        migrate.init_app(app, db)
        ckeditor.init_app(app)
        
        # Configure template settings
        app.jinja_env.add_extension('jinja2.ext.do')
        app.jinja_env.trim_blocks = True
        app.jinja_env.lstrip_blocks = True
        
        # Test database connection
        with app.app_context():
            db.engine.connect()
            logger.info("Database connection successful")
        
        # Register theme context processor
        from utils.theme_manager import inject_theme
        app.context_processor(inject_theme)
        
        # Set default theme colors if not available
        app.context_processor(lambda: {
            'theme_colors': {
                'primary': '#f8f5f2',
                'secondary': '#2c3e50',
                'accent': '#e67e22'
            }
        })
        
        logger.info("Application created successfully")
        return app
        
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        logger.exception("Full traceback:")
        raise

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
        logger.info("Starting extension registration...")
        
        # Import views and routes here to avoid circular imports
        from admin_routes import admin_bp
        logger.info("Admin blueprint imported")
        
        # Register admin blueprint first
        app.register_blueprint(admin_bp)
        logger.info("Admin blueprint registered")
        
        # Import and initialize admin views after blueprint registration
        logger.info("Initializing admin views...")
        import admin_views
        admin = admin_views.init_admin(app)
        logger.info("Admin views initialized successfully")
        
        # Import routes last to avoid circular dependencies
        logger.info("Importing main routes...")
        import routes
        logger.info("Main routes imported successfully")
        
        logger.info("All extensions and blueprints registered successfully")
        return app
    except ImportError as ie:
        logger.error(f"Import error during extension registration: {str(ie)}")
        logger.exception("Import error traceback:")
        raise
    except Exception as e:
        logger.error(f"Error registering extensions: {str(e)}")
        logger.exception("Full error traceback:")
        raise

with app.app_context():
    try:
        # Import models first to ensure all models are defined
        import models
        
        # Register extensions and blueprints
        register_extensions(app)
        logger.info("Extensions registered")
        
        # Create all database tables through migration
        logger.info("Running database migrations...")
        try:
            logger.info("Attempting to connect to database...")
            db.engine.connect()
            logger.info("Database connection successful")
            
            logger.info("Database setup complete")
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}")
            logger.exception("Full traceback:")
            raise
        
        # Set up required directories
        setup_upload_directories()
        logger.info("Upload directories configured")
        
        # Initialize theme system after database is ready
        try:
            from utils.theme_manager import initialize_default_themes
            initialize_default_themes()
            logger.info("Theme initialization completed")
        except Exception as e:
            logger.error(f"Error initializing themes: {str(e)}")
            raise
        
        logger.info("Application initialization complete")
    except Exception as e:
        logger.error(f"Error during application initialization: {str(e)}")
        raise
