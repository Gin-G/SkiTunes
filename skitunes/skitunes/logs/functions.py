import logging
import logging.config

# Define class to setup logging
# Need to set app configuration for LOG_TYPE and LOG_LEVEL
class LogSetup(object):
    # Launch init_app when an app value is supplied
    def __init__(self, app=None, **kwargs):
        if app is not None:
            self.init_app(app, **kwargs)

    # Function to setup the logging
    def init_app(self, app):
        # Grab the log type configuration value for the app
        log_type = app.config["LOG_TYPE"]
        # Get the logging level configuration value for the app
        logging_level = app.config["LOG_LEVEL"]
        # This next section determines how to handle the logging output
        # https://docs.python.org/3/library/logging.handlers.html
        # If the log type is not stream, sending log output to streams such as sys.stdout, sys.stderr or any file-like object
        if log_type != "stream":
            try:
                # The app grabs extra config values 
                # Where to store the logs
                log_directory = app.config["LOG_DIR"]
                # What to name the app logs
                app_log_file_name = app.config["APP_LOG_NAME"]
                # What to name nginx logs
                access_log_file_name = app.config["WWW_LOG_NAME"]
            # If there's a key error it's because one of these values is not set so we will log the error
            except KeyError as e:
                exit(code="{} is a required parameter for log_type '{}'".format(e, log_type))
            # Join the file names with the directory
            app_log = "/".join([log_directory, app_log_file_name])
            www_log = "/".join([log_directory, access_log_file_name])
        # If the log type is stream we use the StreamHandler class
        if log_type == "stream":
            logging_policy = "logging.StreamHandler"
        # If the log type is watched we use the WatchedFileHandler class
        elif log_type == "watched":
            logging_policy = "logging.handlers.WatchedFileHandler"
        # Otherwise we set up some parameters for the RotatingFileHandler class
        else:
            log_max_bytes = app.config["LOG_MAX_BYTES"]
            log_copies = app.config["LOG_COPIES"]
            logging_policy = "logging.handelrs.RotatingFileHandler"
        # Standardize the format
        std_format = {
            "formatters": {
                "default": {
                    "format": "[%(asctime)s.%(msecs)03d] %(levelname)s %(name)s:%(funcName)s: %(message)s",
                    "datefmt": "%d/%b/%Y:%H:%M:%S",
                },
                "access": {"format": "%(message)s"},
            }
        }
        # Standardize the loggers
        std_logger = {
            "loggers": {
                "": {"level": logging_level, "handlers": ["default"], "propagate": True},
                "app.access": {
                    "level": logging_level,
                    "handlers": ["access_logs"],
                    "propagate": False,
                },
                "root": {"level": logging_level, "handlers": ["default"]},
            }
        }
        # Standardize the stream handler 
        if log_type == "stream":
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": logging_level,
                        "formatter": "default",
                        "class": logging_policy,
                    },
                    "access_logs": {
                        "level": logging_level,
                        "class": logging_policy,
                        "formatter": "access",
                    },
                }
            }
        # Standardize the watched file handler
        elif log_type == "watched":
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": logging_level,
                        "class": logging_policy,
                        "filename": app_log,
                        "formatter": "default",
                        "delay": True,
                    },
                    "access_logs": {
                        "level": logging_level,
                        "class": logging_policy,
                        "filename": www_log,
                        "formatter": "access",
                        "delay": True,
                    },
                }
            }
        # Otherwise setup a standard handler
        else:
            logging_handler = {
                "handlers": {
                    "default": {
                        "level": logging_level,
                        "class": logging_policy,
                        "filename": app_log,
                        "backupCount": log_copies,
                        "maxBytes": log_max_bytes,
                        "formatter": "default",
                        "delay": True,
                    },
                    "access_logs": {
                        "level": logging_level,
                        "class": logging_policy,
                        "filename": www_log,
                        "backupCount": log_copies,
                        "maxBytes": log_max_bytes,
                        "formatter": "access",
                        "delay": True,
                    },
                }
            }
        # Set log config
        log_config = {
            "version": 1,
            "formatters": std_format["formatters"],
            "loggers": std_logger["loggers"],
            "handlers": logging_handler["handlers"],
        }
        logging.config.dictConfig(log_config)