import numpy as np
import os
import matplotlib.pyplot as plt
import argparse

def save(name='', fmt='png'):
    pwd = os.getcwd()
    iPath = './{}'.format(fmt)
    if not os.path.exists(iPath):
        os.mkdir(iPath)
    os.chdir(iPath)
    plt.savefig('{}.{}'.format(name, fmt), fmt='png')
    os.chdir(pwd)

parser = argparse.ArgumentParser()
parser.add_argument("namefile")
parser.add_argument("namepic")

f = open(parser.parse_args().namefile, 'r')
name_kor = f.readline().split()
X = []
Y = []
Z = []
for line in f:
    s = line.split()
    if not float(s[0]) in X:
        X.append(float(s[0]))
    if not float(s[1]) in Y:
        Y.append(float(s[1]))
    Z.append(1 if s[2] == 'True' else 0)
f.close()

X1, Y1 = np.meshgrid(X, Y)

Z1 = np.array(Z).reshape(len(X),len(Y))
print(Z1)

figure, axes = plt.subplots()
axes.pcolor(X1, Y1, Z1.T)

save(parser.parse_args().namepic)