''' python3 tests.py'''
'''
tests failed 4 from 62:
[7, 9, 11, 13]
'''
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
import os
import sys
import inspect
# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
print(env_dir)
if env_dir not in sys.path:
    sys.path.insert(0, env_dir)

from translator.tokenizer.tokenizer_main import LexNetTokenizer
from env.equation.data.terms.input.wolfram.lex_net_wolfram import LexNetW

from env.equation.equation import Equation
from env.equation.tests_lists import tests_list_main as tests
import traceback
import sympy


def test_one(_id=0, sympy=False, verbose=False,
             EqBilder=Equation, tests=tests):
    eq = EqBilder(tests[_id])
    print("\n=== test %s: %s ===" % (_id, tests[_id]))
    try:
        try:
            eq.parser.parse()
            
        except BaseException as e:
            # print(eq.from_lex)
            # print(eq.from_cyk)
            if verbose:
                print(e)
                traceback.print_exc()
            pass

        eq.replacer.cpp.editor.set_default()
        eq.replacer.cpp.make_cpp()

        print('\noriginal:')
        eq.show_original()
        
        print('\ncpp:')
        eq.replacer.cpp.show_cpp()

        if sympy:
            print("\nsympy:")
            eq.replacer.sympy.make_sympy()
            eq.replacer.sympy.show_sympy()

        return(True)
    except BaseException as e:
        print("fail test %s" % (_id))
        if verbose:
            print(e)
            traceback.print_exc()
        return(False)


def test_all(EqBilder=Equation, tests=tests):

    succesed = []
    failed = []

    for _id, test in enumerate(tests):
        if test_one(_id, EqBilder=EqBilder, tests=tests):
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


def test_lambda():
    # e = Equation("a*c + d*U+f(y,z,)+sin(x)=-cos(x)")
    # e = Equation("f(y,z,)=-(cos(x)+sin(x))")
    # e = Equation("a*(D[U,{x,2}]) + d*D[U,{y,2}]=cos(x)")
    # e = Equation("U'=a*(D[U,{x,2}]) + d*D[U,{y,2}]+cos(x)")
    # e = Equation("a.t = a")
    e = Equation("a[i,j,] = a[j, i,]")
    e.parser.parse()

    print('\noriginal:')
    e.show_original()
    print(e.eq_tree)

    e.args_editor.get_args()
    print("args:")
    print(e.args)

    e.args_editor.get_vars()

    # x, y, z, U, f, d, c, a = sympy.symbols('x y z U f d c a')

    # work also for print:
    a = sympy.Matrix([[0, 1], [1, 0]])
    # e.args_editor.subs(x=x, y=y, z=z, U=U, f=f, d=d, c=c, a=a)
    e.args_editor.subs(a=a, i=0, j=1)
    print("vars:")
    print(e.vars)

    e.slambda.sympy.lambdify_sem()
    out = e.slambda.sympy.lambdify()
    print("\nlambdify:")
    print(out())
    out = e.slambda.sympy.lambdify_call()
    print("\nlambdify_call:")
    print(out)
    
    e.replacer.sympy.make_sympy()
    print("\nrand_sympy")
    print(e.tree.flatten('rand_sympy'))
    # print(e.tree.flatten('sympy'))
    return(e)


def test_rand():
    e = Equation("a*c + d*U+f(y)+sin(x)=cos(x)")
    # e = Equation("a*D[U,{x,2}] + d*D[U,{y,2}]=cos(x)")
    e.parser.parse()

    print("\noriginal")
    e.show_original()

    e.sampling.sympy.sampling_subs()
    print("\nsampling_subs:")
    e.sampling.sympy.show_sampled()

    e.sampling.sympy.sampling_vars()
    print("\nsampling_vars:")
    e.sampling.sympy.show_sampled()

    # substitute U:
    # get_vars alredy called by
    # sampling_subs or sampling_vars:
    U = sympy.symbols('U')
    e.args_editor.subs(U=U)

    e.slambda.sympy.lambdify_sem()
    out = e.slambda.sympy.lambdify()
    print("\nlambdify:")
    print(out())
    
    print("\nvariables:")
    for var in e.vars:
        print(var['variable'])


def test_lex(sent='a*c + d*U+f(y)+sin(x)'):
    
    terms = LexNetW()
    tokenizer = LexNetTokenizer(terms)

    print("\n=== test: %s ===" % (sent))
        
    res = tokenizer.lex(sent)
    
    print("from lex:")
    print(res)


def test_term_cpp_diff(sent="U'=a*(D[U,{x,2}]+ D[U,{y,2}])"):
    
    eq = Equation(sent)

    print("\n=== test: %s ===" % (sent))
    
    eq.parser.parse()

    editor = eq.replacer.cpp.editor
    editor.set_default()
    
    eq.replacer.cpp.make_cpp()

    print('\noriginal:')
    eq.show_original()
        
    print('\ndiff_common:')
    eq.replacer.cpp.show_cpp()

    print("\ndiff_special side 2, btype 1")
    editor.set_diff_type(diffType='pure',
                         diffMethod='special',
                         btype=1, side=2,
                         func="func")
    eq.replacer.cpp.make_cpp()
    eq.replacer.cpp.show_cpp()

    print("\ndiff_special side 3, btype 1")
    editor.set_diff_type(diffType='pure',
                         diffMethod='special',
                         btype=1, side=3,
                         func="func")
    eq.replacer.cpp.make_cpp()
    eq.replacer.cpp.show_cpp()

    print("\ndiff_interconnect side 2")
    editor.set_diff_type(diffType="pure",
                         diffMethod="interconnect",
                         side=2,
                         firstIndex="firstIndex",
                         secondIndexSTR="secondIndex")
    eq.replacer.cpp.make_cpp()
    eq.replacer.cpp.show_cpp()


if __name__ == '__main__':

    # test_term_cpp_diff()
    # test_lex()
    test_all()
    # test_lambda()
    # test_rand()
    # test_one(8, verbose=True)
    # test_one(12, verbose=True)
    # test_one(-1, sympy=True, verbose=True)
