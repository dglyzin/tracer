import sys
from time import sleep

print ("Welcome to job runner!")

percentage = 0
while percentage<100:
    sleep(1)
    percentage= percentage+13
    print ("job done {}%".format(percentage))

print("job finished!")
