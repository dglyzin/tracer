# parser$ python3 -m env.equation_net.tests

import os
import sys
import inspect
# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
# print(env_dir)
if env_dir not in sys.path:
    sys.path.insert(0, env_dir)

from env.equation_net.equation import Equation
from env.equation.tests_lists import tests_list_main
from env.equation.tests import test_one, test_all
from env.equation.tests import test_term_cpp_diff
import traceback


if __name__ == '__main__':

    # test_term_cpp_diff()
    # test_lex()
    # test_one(11, verbose=True, EqBilder=Equation,
    #          tests=tests_list_main)
    # test_all(EqBilder=Equation, tests=tests_list_main)
    # test_lambda()
    # test_rand()
    test_one(-1, tests=tests_list_main,
             EqBilder=Equation, verbose=True)

    # test_one(-2, tests=tests_list_main, sympy=True,
    #          EqBilder=Equation, verbose=True)
    # eq = test_term_cpp_diff(EqBilder=Equation)
