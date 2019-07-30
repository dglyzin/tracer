# parser$ python3 -m translator.tokenizer.patterns.patterns_types.tests.tests_pattern_ex
from translator.tokenizer.patterns.patterns_types.pattern_ex import PatternEx


def test_split():

    '''Test ``split`` for
    term "eq"'''

    p_ex = PatternEx("eq", "Eq(${eqs})Eq")
    p_ex.compile_parts({})
    p_ex.set_grammar_parts({'a': 'a'})
    
    print("\ntest_0: split")
    sent_list = ["(\\for_all A: linear_operaotr(A)) into"
                 + " Eq(A*A.conjugate_transpose() = E)Eq"
                 + "=>"
                 + "hermitian_operator(A)"]
    
    print("\np_ex.parts:")
    print(p_ex.parts)

    print("\nsent")
    print(sent_list)
    
    out = p_ex.split(sent_list)
    print("\nout:")
    print(out)


if __name__ == '__main__':
    
    test_split()
