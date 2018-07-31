import sys
import os
import inspect

# add import's path:
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

parentdir = os.path.dirname(currentdir)
grantparentdir_0 = os.path.dirname(parentdir)
grantparentdir_1 = os.path.dirname(grantparentdir_0)

sys.path.insert(0, parentdir)
sys.path.insert(0, grantparentdir_0)
sys.path.insert(0, grantparentdir_1)

print("sys.path")
print(sys.path)

import equation.tokenizer.lex as lex
from equation.replacer_cpp import CppGen


def test():

    class term():
        pass

    # FOR diff pattern:
    t = term()
    t.name = term()
    l = lex.Lex()
    res = lex.re.search(l.diff_pattern, 'D[U(t-1.1),{x,2}]')
    t.name.lex = [res.string, res, 'diff_pattern']
    print('term.lex:')
    print(t.name.lex)

    gen = CppGen()
    gen.set_vars_indexes(vars_to_indexes=[('U', 0), ('V', 1)])
    gen.set_blockNumber(blockNumber=0)

    gen.set_diff_type(diffType='pure', diffMethod='common')

    gen.add_out_to(t)
    print(t.cpp.out)
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)

    gen.set_diff_type(diffType='pure', diffMethod='special',
                      side=0, func='sin')

    gen.add_out_to(t)
    print(t.cpp.out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)

    gen.set_diff_type(diffType='pure', diffMethod='interconnect',
                      side=0, firstIndex=0, secondIndexSTR=1)

    gen.add_out_to(t)
    print(t.cpp.out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)
    # END FOR

    # FOR Val pattern
    t = term()
    t.name = term()
    l = lex.Lex()
    res = lex.re.search(l.var_pattern, 'U')
    t.name.lex = [res.string, res, 'var_pattern']
    print('term.lex:')
    print(t.name.lex)

    gen.set_vars_indexes(vars_to_indexes=[('U', 0), ('V', 1)])
    gen.add_out_to(t)
    print(t.cpp.out)
    # END FOR

    # FOR coeffs pattern
    t = term()
    t.name = term()
    l = lex.Lex()
    res = lex.re.search(l.coefs_pattern, 'a')
    t.name.lex = [res.string, res, 'coefs_pattern']
    print('term.lex:')
    print(t.name.lex)

    coeffs_to_indexes = [('a', 0), ('b', 1), ('c', 2), ('r', 3)]
    gen.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

    gen.add_out_to(t)
    print(t.cpp.out)
    # END FOR

    # FOR bound pattern 1d
    t = term()
    t.name = term()
    l = lex.Lex()
    print(l.patterns_dict['bdp'])
    res = lex.re.search(l.patterns_dict['bdp'], 'U(t-1.1,{x,0.3})')
    t.name.lex = [res.string, res, 'bdp']
    print('term.lex:')
    print(t.name.lex)

    gen.set_dim(dim=1)
    gen.set_point(point=[3])
    gen.add_out_to(t)
    print(t.cpp.out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)
    # END FOR

    # FOR bound pattern 2d
    t = term()
    t.name = term()
    l = lex.Lex()
    res = lex.re.search(l.patterns_dict['bdp'], 'U(t-1.1,{x,0.3}{y,0.3})')
    t.name.lex = [res.string, res, 'bdp']
    print('term.lex:')
    print(t.name.lex)

    gen.set_dim(dim=2)
    gen.set_point(point=[3, 3])
    gen.add_out_to(t)
    print(t.cpp.out)
    print("for delays:")
    print(gen.global_params.delays_owner_id)
    print(gen.global_params.delays)
    # END FOR
    

if __name__ == '__main__':
    test()
