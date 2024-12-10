import logging
from app import app

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting Event Services website...")
    app.run(host="0.0.0.0", port=3000, debug=True)
