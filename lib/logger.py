"""Logging module"""

import logging
import os
import sys
import traceback
from datetime import datetime


NAME = "app"


def setup_logging(log_dir=None, log_file="run.log",
                  log_level="INFO"):
    """Initializes and configures the loggers that does logging to
    console as well as in the specified file path

    Args:
      log_dir (str): The absolute log directory path. 
                     Default: Current working dir/logs/<timestamp dir>
      log_file (str): Log file name. Default: run.log
      log_level (str): The minimum log level severity that should be considered
                       for logging.
                       Defaults to 'INFO'
    """

    if log_dir is None:
        log_dir = os.path.join(os.getcwd(), "logs",
                               datetime.today().strftime("%Y%m%d_%H%M%S"))

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    abs_log_file_path = os.path.join(log_dir, log_file)

    log_level = getattr(logging, log_level)
    # Custom variables
    logging.marker = "-" * 60
    logging.step = 1
    logging.stage = ''

    # Create the loggers
    logging.app_logger = logging.getLogger(NAME)

    # Remove all existing handlers
    logging.app_logger.handlers = []

    # Disable the root logger
    logging.getLogger().disabled = True

    # Construct the formatter
    formatter = __get_formatter()

    # setup console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logging.app_logger.addHandler(console_handler)

    # setup file handler
    __configure_file_handler(abs_log_file_path)

    # configure logger
    logging.app_logger.setLevel(log_level)
    logging.app_logger.propagate = 0


def __configure_file_handler(abs_log_file_path):
    formatter = __get_formatter()
    # To store all logs of various severity/log level
    file_handler = logging.FileHandler(abs_log_file_path, 'a')
    file_handler.setFormatter(formatter)
    logging.app_logger.addHandler(file_handler)
    sys.stderr = Tee(sys.stderr, file_handler.stream)


def __get_formatter():
    formatter = logging.Formatter('%(asctime)s (%(threadName)s) %(levelname)s '
                                  '[%(file_line)s] : %(message)s')
    return formatter


def INFO(msg):
    """INFO level logging

    Args:
        msg(str): Message to be logged
    """
    logging.app_logger.info(msg, extra=__extra())


def ERROR(msg):
    """ERROR level logging

    Args:
        msg(str): Message to be logged
    """
    logging.app_logger.error(msg, extra=__extra())


def DEBUG(msg):
    """DEBUG level logging

    Args:
        msg(str): Message to be logged
    """
    logging.app_logger.debug(msg, extra=__extra())


def __extra():
    frame = traceback.extract_stack()[-3]
    file_name = frame[0].split("/")[-1]
    file_line = frame[1]
    return {
        'file_line': "%s:%s" % (file_name, file_line)
    }


class Tee(object):
    """This class defines an proxy to redirect stderr to both stderr and file.
    """

    def __init__(self, stream1, stream2):
        """Initialize Tee object
        Args:
          stream1(object): File handle to write to console
          stream2(object): File handle to write to file
        """
        self.stream1, self.stream2 = stream1, stream2

    def write(self, msg):
        """Writes the message to file handles
        Args:
          msg(str): Message to be written
        """
        self.stream1.write(msg)
        self.stream2.write(msg)

    def flush(self):
        """Flush the messages written so far
        """
        self.stream2.flush()


setup_logging()
