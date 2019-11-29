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

    if '--all' in sys.argv or '-a' in sys.argv:
         
        test_all(EqBilder=Equation, tests=tests_list_main)
    
    elif "-t" in sys.argv:
        test_num = sys.argv[sys.argv.index('-t') + 1]
        test_one(_id=int(test_num), tests=tests_list_main,
                 EqBilder=Equation, verbose=True)
    elif "--test" in sys.argv:
        test_num = sys.argv[sys.argv.index('--test') + 1]
        
        test_one(_id=int(test_num), tests=tests_list_main,
                 EqBilder=Equation, verbose=True)
    elif "-i" in sys.argv:
        print("parser console. write 'q' or 'Ctrl+D' to exit.")
        while(True):
            # print("eq?> ", end='\r')
            try:
                eq = input("eq?> ")
                if eq == "q":
                    raise(EOFError)
                elif '"' in eq:
                    eq = eq.split('"')[1]
                test_one(sent=eq, EqBilder=Equation, verbose=True)
            except EOFError:
                print("exiting...")
                break
            except:
                print(sys.last_value)
                print(sys.last_traceback)
    else:
        test_all(EqBilder=Equation, tests=tests_list_main)
        
    # test_term_cpp_diff()
    # test_lex()
    # test_one(11, verbose=True, EqBilder=Equation,
    #          tests=tests_list_main)
    # test_one(0, tests=tests_list_main,
    #          EqBilder=Equation, verbose=True)

    # test_all(EqBilder=Equation, tests=tests_list_main)
    # test_lambda()
    # test_rand()
    # test_one(-1, tests=tests_list_main,
    #          EqBilder=Equation, verbose=True)
    # test_one(-1, tests=tests_list_main, sympy=True,
    #          EqBilder=Equation, verbose=True)
    # eq = test_term_cpp_diff(EqBilder=Equation)
