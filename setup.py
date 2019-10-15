# must be outside hybriddomain
import os
from setuptools import find_packages


# hybriddomain
this_dir = os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__":
    print("this_dir:")
    print(this_dir)
    print("find_packages:")
    print(find_packages('.'))
