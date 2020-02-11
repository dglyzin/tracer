import os
import subprocess


def get_img_filename_avconv():
    '''For createVideoFile func'''
    return("result_" + "%d.png")


def get_mp4_filename():
    return("result.mp4")


class Postproc():
    
    def __init__(self, logger, model_path):
        self.logger = logger
        self.model_path = model_path

    def createVideoFile(self):
        logger = self.logger
        
        logger.info("Creating video file: results %s"
                    % (get_mp4_filename()))
        command = ("avconv -r 5 -loglevel panic -i "
                   + os.path.join(self.model_path, get_img_filename_avconv())
                   + " -pix_fmt yuv420p -b:v 1000k -c:v libx264 "
                   + os.path.join(self.model_path, get_mp4_filename()))
        logger.info(command)
        # PIPE = subprocess.PIPE
        # proc = subprocess.Popen(command, shell=True, stdin=PIPE,
        #                         stdout=PIPE, stderr=subprocess.STDOUT)
        # proc.wait()
        subprocess.call(command, shell=True)
        logger.info("postproc Done")
