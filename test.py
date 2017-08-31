# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
import os
import argparse
import logging
import json


parser = argparse.ArgumentParser(description='Tracer tester.', epilog="Have fun! XD")
parser.add_argument('-nodecount', type=int, default=4, help="Number of available nodes to run tests on.")
parser.add_argument('-folder', type=str, default="regression",
                    help="Folder to search tests in (including subfolders).")
parser.add_argument('-norun', help="Do not make runs, only compare existing data.", action="store_true")
parser.add_argument('-debug', help="add this flag to run program in debug partition", action="store_true")
args = parser.parse_args()
path = args.folder
logging.basicConfig(filename=os.path.join(path, 'regression.log'), filemode='w', level=logging.DEBUG)
logging.info("Regression tests started")
for root, dirs, files in os.walk(path):
    for specfile in files:
        if specfile.endswith("test.spec"):
            print(os.path.join(root, specfile))
path_test_folder = "regression/String1"


def pullData():
    with open("regression/test.spec", 'r') as fjson:
        data = json.load(fjson)
    return data
data = pullData()

def difference(path_test_folder):
    folder_list = os.listdir(path_test_folder)
    non_ref_file = os.path.join(path_test_folder, list(filter(lambda x: x.startswith('NonRef'), folder_list))[0])
    refFile = os.path.join(path_test_folder, list(filter(lambda x: x.startswith('Ref'), folder_list))[0])
    comp_file = open(refFile, "r")
    comp_read = comp_file.readlines()
    comp_file2 = open(non_ref_file, "r")
    comp2_read = comp_file2.readlines()
    left_delim = comp_read[0].rfind('[')
    n = len(comp_read)
    m = len(comp_read[0][left_delim + 1:-2].split(","))
    diff = np.zeros((n, m))
    abs_max_diff = np.zeros(n)
    for i in range(n):
        for j in range(m):
            diff[i, j] = np.abs(float(comp_read[i][left_delim + 1:-2].split(",")[j]) -
                                float(comp2_read[i][left_delim + 1:-2].split(",")[j]))
        abs_max_diff[i] = max(diff[i, :])
    return (abs_max_diff, n)


abs_max_diff, n = difference(path_test_folder)


def plotter(abs_max_diff, n):
    font = {'family': 'serif',
            'color': 'red',
            'weight': 'normal',
            'size': 16,
            }
    X = np.linspace(0, n, n, endpoint=True)
    plt.plot(X, abs_max_diff, 'g^')
    plt.ylabel('Abs(Max Error)')
    plt.xlabel('t')
    if max(abs_max_diff) > 0.1:
        plt.title('!!!ALARM!!! \n Abs(MaxError) > 0.1', fontdict=font)
    plt.show()


plotter(abs_max_diff, n)