from equation import Equation

def test():

    # s = sys.argv[sys.argv.index('-s')+1]
    input_word_lex = ("a+U*U(t-3.1)*V(t-3.3)+D[V(t-1.1),{y,1}]"
                      + "-c*D[U(t-1.3),{x,2}]")
    input_word_lex_pow = "a+(D[V(t-1.1),{y,1}]-c*D[U(t-1.3),{x,2}])^3"
    input_word_lex_func = "sin(a+c)+cos(U-c*D[U,{x,2}])"
    eq1 = Equation(input_word_lex)
    eq2 = Equation(input_word_lex_pow)
    eq3 = Equation(input_word_lex_func)
    eqs = [eq1, eq2, eq3]

    for eq in eqs:
        eq.set_dim(dim=2)
        eq.set_blockNumber(blockNumber=0)

        eq.set_vars_indexes(vars_to_indexes=[('U', 0), ('V', 1)])

        coeffs_to_indexes = [('a', 0), ('b', 1), ('c', 2)]
        eq.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

        eq.set_diff_type(diffType='pure',
                         diffMethod='common')
        eq.set_point(point=[3, 3])

        eq.parse()
    
    print("\ndelay word_lex_test:")
    print("\ninput: %s\n" % (input_word_lex))
    print('out:')
    eqs[0].show()

    print("\npow word_lex_pow:")
    print("\ninput: %s\n" % (input_word_lex_pow))
    print('out:')
    eqs[1].show()

    print("\nresult word_lex_func:")
    print("\ninput: %s\n" % (input_word_lex_func))
    print('out:')
    eqs[2].show()

    
if __name__ == '__main__':
    test()

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
