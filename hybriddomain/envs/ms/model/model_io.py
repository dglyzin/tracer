import os
import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
logger = logging.getLogger('model_main.model_io')


class ModelIO():
   
    def __init__(self, net):
        self.net = net
        
    def loadFromFile(self, project_folder):
        
        self.net.project_folder = project_folder
        self.net.project_path = project_folder.split('problems/')[-1]
        logger.debug("project_path:")
        logger.debug(self.net.project_path)
        # self.net.project_path = project_folder.replace('problems/', "")
        self.net.project_name = os.path.basename(self.net.project_path)
