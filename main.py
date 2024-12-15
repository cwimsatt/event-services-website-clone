import logging
import sys
from app import app

# Setup logging with more detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Event Services website...")
    try:
        # Test template rendering before starting
        with app.app_context():
            logger.info("Testing template rendering...")
            # Render a simple template to verify Jinja setup
            app.jinja_env.get_template('base.html')
            logger.info("Template rendering test successful")
        
        # Start the application
        logger.info("Starting Flask application server...")
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        logger.exception("Full traceback:")
        sys.exit(1)
