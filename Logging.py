from loguru import logger
import sys

def setup_logger(log_file):
    # Create a custom logger with your desired configuration
    custom_logger = logger
    custom_logger.remove()  # Remove the default handler
    
    # Configure the log file handler
    custom_logger.add(log_file, level="DEBUG", rotation="10 MB")  # Log to a file with rotation

    # Configure console output with colors
    custom_logger.add(sys.stdout, colorize=True, format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>')
    custom_logger.level("DEBUG", color="<yellow>")
    return custom_logger