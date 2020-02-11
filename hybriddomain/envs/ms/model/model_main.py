from hybriddomain.envs.ms.model.model_io import ModelIO

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('model_main')
logger.setLevel(level=log_level)


class ModelNet():
    def __init__(self):
        self.io = ModelIO(self)

