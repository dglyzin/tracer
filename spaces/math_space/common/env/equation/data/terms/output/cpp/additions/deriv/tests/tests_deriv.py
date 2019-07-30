'''
hybriddomain$ python3 -m spaces.math_space.common.env.equation\
.data.terms.output.cpp.additions.deriv.tests.tests_deriv
'''
import sys
if 'spaces/math_space/common' not in sys.path:
    sys.path += ['spaces/math_space/common']

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_common import GenPureCommon

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_borders import GenPureBorders

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_ics import GenPureIcs

from env.equation.data.terms.output.cpp \
    .additions.deriv.gen_pure_vertexs import GenPureVertexs

from env.equation.data.terms.output.cpp \
    .additions.deriv.tests.tests_list import vertexs_asserted

from env.equation.data.terms.output.cpp \
    .additions.deriv.tests.tests_list import ics_asserted

from env.equation.data.terms.output.cpp \
    .additions.deriv.tests.tests_list import borders_asserted

from env.equation.data.terms.output.cpp \
    .additions.deriv.tests.tests_list import common_asserted


def tests_pure_common(use_asserted):

    print("\n=========tests pure common========\n")
    blockNumber = 0
    var = 'U'
    unknownVarsIndexs = dict([('U', 0), ('V', 1)])
    unknownVarIndex = unknownVarsIndexs[var]
    indepVars = ('x', 'y')
    orders = [dict([('x', 1), ('y', 1)]),
              dict([('x', 2), ('y', 2)])]

    print("\ninput:\n")
    print("blockNumber: %s" % blockNumber)
    print("unknownVarIndex: %s" % unknownVarIndex)

    failed = []
    i = 0
    for indepVarOrders in orders:
        for indepVar in indepVars:
            print("\ninput:")
            print("indepVarOrders: %s" % str(indepVarOrders))
            print("indepVar: %s" % indepVar)

            gen = GenPureCommon(blockNumber, unknownVarIndex,
                                indepVar, indepVarOrders)
            out = gen.common_diff()
            print("\nout:\n")
            print(out)

            if use_asserted:
                # FOR check correctness:
                asserted = (out == common_asserted[i])
                print("\nasserted:")
                print(asserted)
                if not asserted:
                    failed.append((i, out))
                # END FOR
            i += 1

    return(failed)


def tests_pure_borders(use_asserted):

    print("\n==========test pure borders:=========\n")
    blockNumber = 0
    var = 'U'
    unknownVarsIndexs = dict([('U', 0), ('V', 1)])
    unknownVarIndex = unknownVarsIndexs[var]
    indepVars = ('x', 'y')
    orders = [dict([('x', 1), ('y', 1)]),
              dict([('x', 2), ('y', 2)])]
    sides = [0, 1, 2, 3]
    border_func = "sin(x)"

    print("\ninput:\n")
    print("blockNumber: %s" % blockNumber)
    print("unknownVarIndex: %s" % unknownVarIndex)
    print("border func: %s" % border_func)

    failed = []
    i = 0
    for indepVarOrders in orders:
        for indepVar in indepVars:
            for side in sides:
                print("\ninput:")
                print("indepVarOrders: %s" % str(indepVarOrders))
                print("indepVar: %s" % indepVar)
                print("side: %s" % side)
                gen = GenPureBorders(blockNumber, unknownVarIndex,
                                     indepVar, indepVarOrders)
                gen.set_special_params(side)
                out = gen.borders_diff(border_func)
                print("\nout:\n")
                print(out)

                if use_asserted:
                    # FOR check correctness:
                    asserted = (out == borders_asserted[i])
                    print("\nasserted:")
                    print(asserted)
                    if not asserted:
                        failed.append((i, out))
                    # END FOR
                i += 1
    return(failed)


def tests_pure_ics(use_asserted):

    print("\n==========test pure ics:=========\n")
    blockNumber = 0
    var = 'U'
    unknownVarsIndexs = dict([('U', 0), ('V', 1)])
    unknownVarIndex = unknownVarsIndexs[var]
    indepVars = ('x', 'y')
    orders = [dict([('x', 1), ('y', 1)]),
              dict([('x', 2), ('y', 2)])]
    sides = [0, 1, 2, 3]
    firstIndex = 'firstIndex'
    secondIndexSTR = 'secondIndexSTR'

    print("\ninput:\n")
    print("blockNumber: %s" % blockNumber)
    print("unknownVarIndex: %s" % unknownVarIndex)

    failed = []
    i = 0
    for indepVarOrders in orders:
        for indepVar in indepVars:
            for side in sides:
                print("\ninput:")
                print("indepVarOrders: %s" % str(indepVarOrders))
                print("indepVar: %s" % indepVar)
                print("side: %s" % side)
                gen = GenPureIcs(blockNumber, unknownVarIndex,
                                 indepVar, indepVarOrders)
                gen.set_special_params(side, firstIndex, secondIndexSTR)
                out = gen.ics_diff()
                print("\nout:\n")
                print(out)

                if use_asserted:
                    # FOR check correctness:
                    asserted = (out == ics_asserted[i])
                    print("\nasserted:")
                    print(asserted)
                    if not asserted:
                        failed.append((i, out))
                    # END FOR
                i += 1
    return(failed)


def tests_pure_vertexs(use_asserted):

    print("\n==========test pure vertexs:=========\n")
    blockNumber = 0
    var = 'U'
    unknownVarsIndexs = dict([('U', 0), ('V', 1)])
    unknownVarIndex = unknownVarsIndexs[var]
    indepVars = ('x', 'y')
    orders = [dict([('x', 1), ('y', 1)]),
              dict([('x', 2), ('y', 2)])]
    vertexs_sides = [[0, 2], [2, 1], [1, 3], [3, 0]]
    border_func = "sin(x)"

    print("\ninput:\n")
    print("blockNumber: %s" % blockNumber)
    print("unknownVarIndex: %s" % unknownVarIndex)
    print("border func: %s" % border_func)

    failed = []
    i = 0
    for indepVarOrders in orders:
        for indepVar in indepVars:
            for vertex_sides in vertexs_sides:

                print("\ninput:")
                print("indepVarOrders: %s" % str(indepVarOrders))
                print("indepVar: %s" % indepVar)
                print("vertex_sides: %s" % vertex_sides)
                gen = GenPureVertexs(blockNumber, unknownVarIndex,
                                     indepVar, indepVarOrders)
                gen.set_special_params(vertex_sides)
                out = gen.vertexs_diff(border_func)
                print("\nout:\n")
                print(out)

                if use_asserted:
                    # FOR check correctness:
                    asserted = (out == vertexs_asserted[i])
                    print("\nasserted:")
                    print(asserted)
                    if not asserted:
                        failed.append((i, out))
                    # END FOR
                i += 1
    return(failed)


if __name__ == "__main__":

    # faileds = tests_pure_common(True)
    # faileds = tests_pure_borders(True)
    # faileds = tests_pure_ics(True)
    faileds = tests_pure_vertexs(True)

    for failed in faileds:
        print("/n fail:")
        print(failed)

