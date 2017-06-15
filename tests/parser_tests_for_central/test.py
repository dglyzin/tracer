import os
from domainmodel.equation import Equation
import tests.introduction.part_2_generators as p2


def test_sample():
    print("test")


def test_delay_eqs():
    '''
    DESCRIPTION:
    Test some equations (from string)
    to .cpp file in
    "hybriddomain/tests/parser_tests_for_central/src/"
    folder.
    '''
    eqStrList = [u"U'=a*(D[U(t-1),{y,2}])",
                 u"U'=a*(D[U,{y,2}])+U(t-3)",
                 u"U'=a*(D[U(t-2),{y,3}])+U(t-3)",
                 u"U'=a*(D[U(t-1),{y,2}] + D[U(t-5),{x,1}])"]
    eqList = []
    for eqStr in eqStrList:
        e = Equation("test")
        e.vars = [u'x', u'y']
        e.system = [eqStr]
        eqList.append(e)

    # parser equations
    out = p2.test_gen_central(eqList)
    
    # write to file
    f = open(os.path.join(os.getcwd(), 'tests',
                          'parser_tests_for_central',
                          'src', 'some_central_functions.cpp'),
             'w')
    f.write(out)
    f.close()
