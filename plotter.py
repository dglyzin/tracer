'''
Created on Mar 2, 2017

@author: dglyzin
'''



import argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import cm



from domainmodel.model import Model

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Creating pictures and a movie for a given folder.', epilog = "Have fun!")
    #mandatory argument, project folder
    parser.add_argument('projectDir', type = str, help = "local folder to process")
    #mandatory argument, project name without extension
    parser.add_argument('projectName', type = str, help = "project name without extension")
    args = parser.parse_args()
        
    createMovie(args.projectDir, args.projectName)