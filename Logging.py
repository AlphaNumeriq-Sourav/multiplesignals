
import logging
import sys


def setup_logger(FileName , LoggerName):
    # Create logger
    logger = logging.getLogger(LoggerName)
    logger.setLevel(logging.DEBUG)

    # Create file handler and set level to DEBUG
    fh = logging.FileHandler(FileName)
    fh.setLevel(logging.DEBUG)

    # Create console handler and set level to INFO
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Define a formatter for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set formatter for the file handler
    fh.setFormatter(formatter)

    # For terminal/console output, use a formatter with color codes
    class ColoredFormatter(logging.Formatter):
        BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
        COLORS = {
            'DEBUG': BLUE,
            'INFO': GREEN,
            'WARNING': YELLOW,
            'ERROR': RED,
            'CRITICAL': RED,
        }

        def format(self, record):
            log_message = super(ColoredFormatter, self).format(record)
            color_code = self.COLORS.get(record.levelname, self.WHITE)
            return f"\033[1;3{color_code}m{log_message}\033[0m"

    # Set formatter for the console handler
    colored_formatter = ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(colored_formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)




# def setup_logger(log_file):
#     # Create a custom logger with your desired configuration
#     custom_logger = logger
#     custom_logger.remove()  # Remove the default handler
    
#     # Configure the log file handler
#     custom_logger.add(log_file, level="DEBUG", rotation="10 MB")  # Log to a file with rotation

#     # Configure console output with colors
#     custom_logger.add(sys.stdout, colorize=True, format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>')
#     custom_logger.level("DEBUG", color="<yellow>")
#     return custom_logger