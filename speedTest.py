import sys
import subprocess

argc = len(sys.argv)
connection = sys.argv[argc-2]
repeatCount = int(sys.argv[argc-1])

for i in range(1, argc - 2):
    for j in range(repeatCount):
        command = "python remoterun.py " + sys.argv[i] + " " + connection
        print command
        subprocess.call(command, shell=True)