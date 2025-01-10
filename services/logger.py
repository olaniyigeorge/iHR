import logging
import sys

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s")

# Create and configure stream handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

# Create and configure file handler
file_handler = logging.FileHandler("/logs/server.logs")
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.handlers = [stream_handler, file_handler]

