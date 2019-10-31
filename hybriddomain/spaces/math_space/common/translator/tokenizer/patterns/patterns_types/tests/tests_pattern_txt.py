# parser$ python3 -m translator.tokenizer.patterns.patterns_types.tests.tests_pattern_txt
from translator.tokenizer.patterns.patterns_types.pattern_txt import PatternTxt


def get_tests_grammar_parts():
    grammar_parts = {'a': 'a',
                     'br': {'br_left':
                            {'left': 'f(',
                             'mid': ',',
                             'right': ')'},
                            'br_mid':
                            {'mid': ')f('},
                            'br_right':
                            {'left': '(',
                             'mid': ',',
                             'right': ')w'}}}
    return(grammar_parts)


def test_0():

    '''Test ``compile_parts``
    for term ``p_act``'''

    print("\ntest_0: compile_parts")

    p_act = PatternTxt('action', r"act ${{action_type}} ",
                       'a')
    
    subterms_values = {'action_type': r"rotate ${{obj}}",
                       'obj': r"sphere"}
    p_act.compile_parts(subterms_values)
    test_0 = p_act.value_lex
    print("\ntest_0 out:")
    print(test_0)


def test_1():

    '''Test ``get_vector``
    for term ``p_cond_all``'''

    print("\ntest_1: get_vector")

    p_cond_all = PatternTxt('cond_all', r"\for_all${in}:${norm}",
                            'br_left', [True, True, False])
    subterms_grammar_values = {'in': 'a', 'norm': 'a'}

    test_3 = p_cond_all.get_vector(subterms_grammar_values)
    print("\ntest_3 out:")
    print(test_3)


def test_2():

    '''Test ``get_splited``
    for term ``p_cond_all``'''

    print("\ntest_2: get_splited")

    p_cond_all = PatternTxt('cond_all', r"\for_all${in}:${norm}",
                            'br_left', [True, True, False])

    print("\np_cond_all.subterm_pattern_cell_group:")
    print(p_cond_all.subterm_pattern_cell_group)
    print("\np_cond_all.template:")
    print(p_cond_all.template)
    test_2 = p_cond_all.get_splited(group=True)
    print("\nget_splited(group=True)")
    print(test_2)
    print(p_cond_all.subterm_pattern_cell)
    test_2 = p_cond_all.get_splited(group=False)
    print("\nget_splited(group=False)")
    print(test_2)


def test_3():

    '''Test ``get_splited``
    for term ``p_in``'''

    print("\ntest_3: get_splited")

    p_in = PatternTxt('in', r"${var}\in${var}", 'br_mid')
    
    print(p_in.subterm_pattern_cell_group)
    test_3 = p_in.get_splited(group=True)
    print("get_splited(group=True)")
    print(test_3)
    print(p_in.subterm_pattern_cell)
    test_3 = p_in.get_splited(group=False)
    print("get_splited(group=False)")
    print(test_3)


def test_4():

    '''Test ``parts and map_ptg``
    for term ``p_cond_all``'''

    p_cond_all = PatternTxt('cond_all', r"\for_all${in}:${norm}",
                            'br_left', [True, True, False])

    print("\ntest_4: %s" % (p_cond_all.template))

    grammar_parts = get_tests_grammar_parts()
    p_cond_all.set_grammar_parts(grammar_parts)
    print("parts:")
    print(p_cond_all.parts)
    print("map_ptg:")
    print(p_cond_all.map_ptg)


def test_5():

    '''Test ``parts and map_ptg``
    for term ``p_in``'''

    grammar_parts = get_tests_grammar_parts()
    p_in = PatternTxt('in', r"${var}\in${var}", 'br_mid')
    p_in.set_grammar_parts(grammar_parts)

    print("\ntest_5: %s" % (p_in.template))

    p_in.set_grammar_parts(grammar_parts)
    print("parts:")
    print(p_in.parts)
    print("map_ptg:")
    print(p_in.map_ptg)


def test_6():

    '''Test ``split_part``
    for term ``p_act``'''

    print("\ntest_6.0: compile_parts")

    p_act = PatternTxt('action', r"act ${{action_type}} ",
                       'a')

    subterms_values = {'action_type': r"rotate ${{obj}}",
                       'obj': r"sphere"}
    p_act.compile_parts(subterms_values)

    print('\n test_6.1: %s' % (p_act.value_lex))

    grammar_parts = get_tests_grammar_parts()
    sent = ("in act rotate sphere at 30"
            + " and act rotate sphere at 31")
    print("sent: %s" % (sent))
    p_act.set_grammar_parts(grammar_parts)
    out = p_act.split_part(p_act.value_lex, sent)
    print(out)


def test_7():

    '''Test ``split_part``
    for term ``p_in`` and ``p_cond_all``'''

    sent = r'\for_all x \in X: x == y'

    p_in = PatternTxt('in', r"${var}\in${var}", 'br_mid')

    p_cond_all = PatternTxt('cond_all', r"\for_all${in}:${norm}",
                            'br_left', [True, True, False])
    
    grammar_parts = get_tests_grammar_parts()
    p_in.set_grammar_parts(grammar_parts)
    p_cond_all.set_grammar_parts(grammar_parts)

    print('\n test_7: %s' % (p_cond_all.template))

    out = p_cond_all.split_part(r'\for_all', sent)
    print(out)
    print("split with ':'")
    out = p_cond_all.split_part(r':', sent)
    print(out)

    print('\n test_7.1: %s' % (p_in.template))
    print("split with '\in'")
    out = p_in.split_part(r'\in', sent)
    print(out)


def test_8():

    '''Test ``split_part``
    for term ``p_pow``'''
    
    p_pow = PatternTxt('pow', r'^', 'br_right',
                       [False, False, True])

    print('\n test_8: %s' % (p_pow.template))
    grammar_parts = get_tests_grammar_parts()
    p_pow.set_grammar_parts(grammar_parts)
    print("parts:")
    print(p_pow.parts)
    print("map_ptg:")
    print(p_pow.map_ptg)

    sent = r'f(n) = n^5 + 4n^2 + 2 |_{n=17}'

    print('\n test_8.1: split_part')
    sent = r'f(n) = n^5 + 4n^2 + 2 |_{n=17}'
    print("sent: %s" % (sent))
    out = p_pow.split_part(r'^', sent)
    print(out)

    print('\n test_8.2: %s' % (p_pow.template))
    sent = r'^5'
    print("sent: %s" % (sent))
    out = p_pow.split_part(r'^', sent)
    print(out)


def test_9():
    
    '''Test ``split_part``
    for term ``p_in``'''
    
    p_in = PatternTxt('in', r"${var}\in${var}", 'br_mid')
    grammar_parts = get_tests_grammar_parts()
    p_in.set_grammar_parts(grammar_parts)

    print('\n test_9: %s' % (p_in.template))
    sent = r'\in'
    print("sent: %s" % (sent))
    out = p_in.split_part(r'\in', sent)
    print(out)

    print('\n test_9.1: %s' % (p_in.template))
    sent = r''
    print("sent: %s" % (sent))
    out = p_in.split_part(r'\in', sent)
    print(out)


def test_10():
    
    '''Test ``split_part``
    for term ``p_cond_all``'''
    
    p_cond_all = PatternTxt('cond_all', r"\for_all${in}:${norm}",
                            'br_left', [True, True, False])
    
    grammar_parts = get_tests_grammar_parts()
    p_cond_all.set_grammar_parts(grammar_parts)

    print('\n test_10: %s' % (p_cond_all.template))
    sent = "a:b:c \in C"
    print("sent: %s" % (sent))
    out = p_cond_all.split_part(r':', sent)
    print(out)


def test_11():
    
    '''Test ``split``
    for term ``p_cond_all``'''
    
    p_in = PatternTxt('in', r"${var}\in${var}", 'br_mid')
    p_cond_all = PatternTxt('cond_all', r"(\for_all${in}:${norm}",
                            'br_left', [True, True, False])

    grammar_parts = get_tests_grammar_parts()
    p_in.set_grammar_parts(grammar_parts)
    p_cond_all.set_grammar_parts(grammar_parts)

    print('\n test_11.0: %s' % (p_cond_all.template))
    sent = ['(\\for_all x \in X: x == y)']
    print("sent: %s" % (str(sent)))
    out = p_cond_all.split(sent)
    print(out)
    
    print('\n test_11.1: %s' % (p_cond_all.template))
    sent = ['(\\for_all x \in X: x == y) and (\\for_all y \in Y: y == z)']
    print("sent: %s" % (str(sent)))
    out = p_cond_all.split(sent)
    print(out)


def tests_base():
    
    print("\n======== FOR: base tests =========")
    test_0()
    test_1()
    test_2()
    test_3()
    print("\n======== END FOR: base tests =========")


def tests_parts_and_map_ptg():

    print("\n======== FOR: parts and map_p tests =========")
    test_4()
    test_5()
    print("\n======== END FOR: parts and map_ptg tests =========")


def tests_split_part():
    print("\n======== FOR: split_sent_part tests =========")
    test_6()
    test_7()
    test_8()
    test_9()
    test_10()
    print("\n======== END FOR: split_sent_part tests =========")
    

def tests_split():

    print("\n======== FOR: pattern split tests =========")
    test_11()
    print("\n======== END FOR: pattern split tests =========")


if __name__ == '__main__':
    
    tests_base()
    tests_parts_and_map_ptg()
    tests_split_part()
    tests_split()
