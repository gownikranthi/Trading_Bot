import logging
from logging.handlers import RotatingFileHandler
import json
import sys

# Define a custom JSON formatter
class JsonFormatter(logging.Formatter):
    """
    Custom logging formatter that outputs log records as JSON.
    This provides a structured format that is easy to parse and analyze.
    """
    def format(self, record):
        # Create a dictionary for the log record
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.name,
            "event": record.getMessage(),
            "details": record.details if hasattr(record, 'details') else None,
            "error_trace": record.exc_text if record.exc_info else None,
        }
        # Dump the dictionary to a JSON string
        return json.dumps(log_record)

def setup_logger():
    """
    Sets up a rotating file logger for the bot.
    Logs are written to 'bot.log' in a structured JSON format.
    The log file will rotate when it reaches 5MB, keeping up to 5 backups.
    """
    # Create logger instance
    logger = logging.getLogger('binance_bot_logger')
    logger.setLevel(logging.INFO)

    # Use a specific format for the timestamp, e.g., ISO8601
    formatter = JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z")

    # Create a rotating file handler
    log_file = "bot.log"
    # MaxBytes is 5MB, backupCount is 5
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(file_handler)

    # Also add a stream handler for console output during development
    stream_handler = logging.StreamHandler(sys.stdout)
    # A simple formatter for console readability
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logger.addHandler(stream_handler)

    return logger

# Create a logger instance on module load
logger = setup_logger()
