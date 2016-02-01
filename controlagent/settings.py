import os
import logging
import logging.config
from configparser import RawConfigParser


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "configs")

config = RawConfigParser()
config.read(os.path.join(CONFIG_DIR, "config.ini"))

SERVER = {
	'host': config.get("server", "host"),
	'port': config.get("server", "port")
}

DEBUG = config.getboolean("server", "debug")

loggingConfig = { 
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'console': { 
            'format': '[%(asctime)s]: %(message)s'
        },
    },
    'handlers': { 
        'controle_node.request': { 
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': "console"
        },
    } 
}

logging.config.dictConfig(loggingConfig)
