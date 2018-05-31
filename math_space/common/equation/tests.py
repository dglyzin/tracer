''' python3 tests.py'''
'''
eq1 = Eq("U'=a*(U(t-3.1)+U(t-1.1))")
# ...
ereg1 = eRegion(equation=eq1,
                begin=[0.5, 0.0], end=[2.7, 1])
# ...
bound1 = Dirichlet(begin, end, func='sin(y)')
side0 = Side()
side0.set_bound(bound1, coords=[[x1, x2],...])
side0.set_default(bound0)
# ...
ireg1 = IRegion(val='0')
# ...

block1 = Block(size=[]
               sides=[side0, ...],
               equationRegions=[ereg1, ereg2, ereg3],
               initRegions = [ireg1])
# ...
ic1 = Interconnects(blocks=[block1, block2],
                    sides=[1, 0])

model = Model(grid, blocks=[block1,...],
              ics=[ic1,...])
domain = model.gen_domain('hybridsolver')
src = model.gen_cpp('hybridsolver')
solver.run(domain, src)
'''
from math_space.common.equation.equation import Equation

import traceback


tests = ["(U)^3",
         "(V(t-1.1, {x, 0.7}{y, 0.7}))^3",
         "(D[V(t-1.1), {x, 2}])^3",
         '(U(t-1))^3',
         "D[U(t-1.1), {x,2}]+D[U(t-5.1), {y,2}]+D[V(t-1.1), {x,1}]",
         "-U(t,{x, a})",
         "-U(t,{x, 0.7}{y, 0.7})",
         "-V(t-1.1, {x, a}{y, 0.7})",
         "-(V+U)",
         "-W(t, {x, 0.7}{y, 0.3})",
         "-U(t-1.1, {x, 0.7}{y, 0.3})",
         "f(x, y)*t",

         "U'=a+U+U*U*V-(b+1)*U+c*D[U,{x,2}]",
         "U'=a+U*U*V-(b+1)*U+c*D[U,{x,2}]",
         "U",
         "U'=a+U*U*V-(b+1)*U+c*D[U,{x,2}]",
         "U'=a+U*U*V-(b+1)*U+c*(D[U,{x,2}]+D[U,{y,2}])",
         "U'=a+U*U*V-(b+1)*U+c*(D[U,{x,2}]+D[U,{y,2}])",
         "U'= a * D[U,{x,2}]",
         "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
         "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
         
         "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
         "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
         "U'= 0",
         "U'= b * (D[U,{x,2}] + D[U,{y,2}])",
         "U'= a * (D[U,{x,2}] + D[U,{y,2}])",
         "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
         "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
         "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
         "U'= D[U,{x,2}]",
         "U'=a*D[U,{x,2}]+ r*U*(1-U(t-1))",
         "U'=a*D[U,{x,2}]+ r*U*(1-U(t-1))",
         "U'= D[U,{x,2}] + D[V,{x,2}]",
         "U'=a*D[U,{x,2}] + d*U",
         "U(t,{x,0.7}{y, 0.7})",
         "U'=a*D[U,{x,2}]",
         "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
         "U'=a*(D[U,{x,2}]+D[U,{y,2}])+U(t-3.1)+U(t-1.3)",
         "U'= D[U,{x,2}]",
         "U'=2.0 - V",
         "(U(t-1.3,{x, 0.7}{y,0.3}))",
         "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
         "U",
         "U'=a * (D[U,{x,2}] + D[U,{y,2}])",
         "U'=b * (D[U,{x,2}] + D[U,{y,2}])",
         "U'=a+U*U*V-(b+1)*U+c*(D[U,{x,2}]+D[U,{y,2}])",
         "U'=a * (D[U,{x,2}] + D[U,{y,2}])",
         "U'=2.0 - V",
         "U'=a*(D[U,{x,2}] + D[U,{y,2}])",
         "U'=a*(sin(a+b)+(U)^3)",
         ("(V(t-3.1)*U(t-3.1)+V(t-1.1)*U(t-3.1)+U(t-1.1))^3"
          + "+cos(U-c*D[U,{x,2}])"),
         ("U'=(V(t-3.1)*U(t-3.1)+V(t-1.1)*U(t-3.1)+U(t-1.1))^3"
          + "+cos(U-c*D[U,{x,2}])"),
         "U'=U",
         "U'=-U",
         "U'=-(U+V)",
         "U",
         "-(U(t-1.1)+V)",
         "U'=-(U(t-1.1)+V)",
         "f(x, y,)+g(y,z,)+h(x,z,)"]


def test_one(test, _id=0, verbose=False):
    eq = Equation(test)
    print("\n=== test %s: %s ===" % (_id, tests[_id]))
    try:
        try:
            eq.parse()
        except BaseException as e:
            # print(eq.from_lex)
            # print(eq.from_cyk)
            if verbose:
                print(e)
                traceback.print_exc()
            pass

        eq.set_default()

        print('\noriginal:')
        eq.show_original()
        
        print('\ncpp:')
        eq.show_cpp()
        return(True)
    except BaseException as e:
        print("fail test %s" % (_id))
        if verbose:
            print(e)
            traceback.print_exc()
        return(False)


def test_all():

    succesed = []
    failed = []

    for _id, test in enumerate(tests):
        if test_one(test, _id):
            succesed.append(_id)
        else:
            failed.append(_id)

    print("\ntests failed %s from %s:"
          % (len(failed), len(failed)+len(succesed)))
    print(failed)
    
    '''
    outs.append(eq.flatten('original')
    outs.append(eq._sym_step(test))

    cpp_fl = flatten(eq.operator_tree, eq.tree_cpp_replacer)
    cpp_fl = eq.operator_tree.flatten('cpp')
    cpp_map = map_tree(eq.operator_tree, eq.tree_cpp_replacer)
    cpp_map_postproc = map_tree_postproc(cpp_map, eq.tree_cpp_replacer)

    print("original:")
    print(cpp_map_postproc.flatten('original'))
    print("cpp:")
    print(cpp_map_postproc.flatten('cpp'))

    return(cpp_map_postproc)
    return(cpp_map)
    return(cpp_fl)
    '''


if __name__ == '__main__':
    test_all()
    # test_one()
