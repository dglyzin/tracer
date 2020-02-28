import os
import subprocess


def get_img_filename_avconv(results_name):
    '''For createVideoFile func'''
    return(results_name+"_" + "%d.png")


def get_mp4_filename(results_name):
    return(results_name+".mp4")


class Postproc():
    
    def __init__(self, logger, model_path,
                 results_name="result"):
        self.logger = logger
        self.model_path = model_path
        self.results_name = results_name

    def createVideoFile(self):
        logger = self.logger
        
        logger.info("Creating video file: results %s"
                    % (get_mp4_filename(self.results_name)))
        command = ("avconv -r 5 -loglevel panic -i "
                   + os.path.join(self.model_path,
                                  get_img_filename_avconv(self.results_name))
                   + " -pix_fmt yuv420p -b:v 1000k -c:v libx264 "
                   + os.path.join(self.model_path,
                                  get_mp4_filename(self.results_name)))
        logger.info(command)
        # PIPE = subprocess.PIPE
        # proc = subprocess.Popen(command, shell=True, stdin=PIPE,
        #                         stdout=PIPE, stderr=subprocess.STDOUT)
        # proc.wait()
        subprocess.call(command, shell=True)
        logger.info("postproc Done")
