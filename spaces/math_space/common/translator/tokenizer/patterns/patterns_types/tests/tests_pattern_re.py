# parser$ python3 -m translator.tokenizer.patterns.patterns_types.tests.tests_pattern_re

from translator.tokenizer.patterns.patterns_types.pattern_re import PatternRe

import re


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

    '''Test ``sub_parts_cells_with_names``'''

    p = PatternRe('arg_time', r"[t](-${{arg_delay}})?",
                  'a')
    '''
    print("\ntest_0:")
    test_0 = p.search('t-arg_delay')
    print(test_1)
    '''
    print("\ntest_0: sub_parts_cells_with_names")
    p.sub_parts_cells_with_names()
    test_0 = p.value_lex
    print(test_0)


def test_1():

    '''Test compile_parts a'''

    print("\ntest_1: compile_parts a")

    p = PatternRe('arg_time', r"[t](-${{arg_delay}})?",
                  'a')
    subterms_values = {'arg_delay': r"(?P<delay>${{float}})",
                       'float': r"\d+\.\d+|\d+"}
    p.compile_parts(subterms_values)
    test_1 = p.value_lex
    print(test_1)


def test_2():

    '''Test get_subparts br'''

    print("\ntest_2: get_subparts br")

    p_cond_all = PatternRe('cond_all', r"${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])
    
    test_2 = p_cond_all.get_subparts()
    print("\ntest_2 out:")
    print(test_2)


def test_3():

    '''Test compile_parts br'''

    print("\ntest_3: compile_parts br")

    p_cond_all = PatternRe('cond_all', r"${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])

    subterms_values = {'for_all': r"\\for_all"}
    p_cond_all.compile_parts(subterms_values)
    test_3 = p_cond_all.value_lex
    print("\ntest_3 out:")
    print(test_3)


def test_3_1():

    '''Test compile_parts br'''

    print("\ntest_3_1: compile_parts br")

    arg_space = PatternRe('arg_space',
                          r"(\{${{free_var}},${{free_var_val}}\})?",
                          'a')
    subterms_values = {
        'free_var_val': r"(?P<val_space>${{int}})",
     
        'free_var': r"[x-z]",
        'int': r"\d+"}

    arg_space.compile_parts(subterms_values)
    
    print("\ntest_3_1 value_lex:")
    print(arg_space.value_lex)
    print("\ntest_3_1 template:")
    print(arg_space.template)


def test_3_2():

    '''Test compile_parts br'''

    print("\ntest_3_2: compile_parts br")

    bound = PatternRe('bound',
                      r"${{var_bdp}}\(${{arg_time}},${{arg_space_bound}}\)",
                      'a')
    subterms_values = {
        'arg_time': r"[${{base_time}}](-${{arg_delay}})?",
        'base_time': r"t",
        'arg_delay': r"(?P<delay>${{arg_float}})",
        'arg_float': r"(?:${{float}})",
        'float': r"\d+\.\d+|\d+",

        'var_bdp': r"(?P<val>[${{base_dep_vars}}])",
        'base_dep_vars': r"A-Z",

        'arg_space_bound': r"(\{${{free_var}},${{arg_float}}\})+",
        'free_var': r"[${{base_indep_vars}}]",
        'base_indep_vars': r"x-z"}

    bound.compile_parts(subterms_values)
    
    print("\ntest_3_2 value_lex:")
    print(bound.value_lex)
    print("\ntest_3_2 template:")
    print(bound.template)
    out = re.search(bound.template, "V(t-1.1,{x,0.7}{y,0.7})")
    print("\nre out:")
    print(out)
    return(bound)


def test_4():
    
    '''Test get_vector'''

    print("\ntest_4: get_vector")
    subterms_grammar_values = {'in': 'a', 'norm': 'a'}
    p_cond_all = PatternRe('cond_all', r"${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])

    subterms_values = {'for_all': r"\\for_all"}
    p_cond_all.compile_parts(subterms_values)
    
    test_4 = p_cond_all.get_vector(subterms_grammar_values)
    print("test_4 out:")
    print(test_4)


def test_5():

    '''Test get_splited'''

    p_cond_all = PatternRe('cond_all', r"${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])

    subterms_values = {'for_all': r"\\for_all"}
    p_cond_all.compile_parts(subterms_values)

    print("\ntest_5: get_splited")
    print(p_cond_all.subterm_pattern_cell_group)
    test_5 = p_cond_all.get_splited(group=True)
    print("\nget_splited(group=True):")
    print(test_5)
    print(p_cond_all.subterm_pattern_cell)
    test_5 = p_cond_all.get_splited(group=False)
    print("\nget_splited(group=False):")
    print(test_5)

    
def test_6():

    '''Test get_splited'''

    p_in = PatternRe('in', r"${var}\\in${var}", 'br_mid')

    print("\ntest_6: get_splited")
    print(p_in.subterm_pattern_cell_group)
    test_6 = p_in.get_splited(group=True)
    print("\nget_splited(group=True):")
    print(test_6)
    print(p_in.subterm_pattern_cell)
    test_6 = p_in.get_splited(group=False)
    print("\nget_splited(group=False):")
    print(test_6)


def test_7():

    '''Test ``set_grammar_parts`` for term ``p_cond_all``'''

    p_cond_all = PatternRe('cond_all', r"${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])

    print("\ntest_7: %s" % (p_cond_all.template))

    subterms_values = {'for_all': r"\\for_all"}
    p_cond_all.compile_parts(subterms_values)

    grammar_parts = get_tests_grammar_parts()
    p_cond_all.set_grammar_parts(grammar_parts)

    print("parts:")
    print(p_cond_all.parts)
    print("map_ptg:")
    print(p_cond_all.map_ptg)


def test_8():

    '''Test ``set_grammar_parts`` for term ``p_in``'''

    p_in = PatternRe('in', r"${var}\\in${var}", 'br_mid')

    print("\ntest_8: %s" % (p_in.template))

    grammar_parts = get_tests_grammar_parts()

    p_in.set_grammar_parts(grammar_parts)
    print("parts:")
    print(p_in.parts)
    print("map_ptg:")
    print(p_in.map_ptg)


def test_9():

    '''Test ``split_sent_part`` for term
    ``arg_time`` r"[t](-${{arg_delay}})?"
    for sent= " y(t-1.1) == z(t-1.2)"'''

    p = PatternRe('arg_time', r"[t](-${{arg_delay}})?",
                  'a')

    print('\ntest_9.0: %s' % (p.value_lex))
    sent = " y(t-1.1) == z(t-1.2)"
    print("sent: %s" % (sent))

    subterms_values = {'arg_delay': r"(?P<delay>${{float}})",
                       'float': r"\d+\.\d+|\d+"}
    p.compile_parts(subterms_values)

    grammar_parts = get_tests_grammar_parts()

    p.set_grammar_parts(grammar_parts)
    out = p.split_part(p.value_lex, sent)
    print("\ntest_9:")
    print(out)


def test_10():

    '''Test ``split_sent_part`` for term
    ``p_in`` r"${var}\\in${var}"
    and
    ``p_cond_all`` r"${{for_all}}${in}:${norm}"
    for sent= "\\for_all x \in X: x == y"'''

    p_in = PatternRe('in', r"${var}\\in${var}", 'br_mid')
    p_cond_all = PatternRe('cond_all', r"${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])
    sent = '\\for_all x \in X: x == y'

    print("\nsent:")
    print(sent)

    subterms_values = {'for_all': r"\\for_all"}
    p_cond_all.compile_parts(subterms_values)

    grammar_parts = get_tests_grammar_parts()
    p_in.set_grammar_parts(grammar_parts)
    p_cond_all.set_grammar_parts(grammar_parts)

    print('\n test_10.0: %s' % (p_cond_all.template))

    print("split with '\\for_all'")
    out = p_cond_all.split_part(r'\\for_all', sent)
    print(out)
    print("split with ':'")
    out = p_cond_all.split_part(r':', sent)
    print(out)

    print('\n test_10.1: %s' % (p_in.template))
    print("split with '\\in'")
    p_in.set_grammar_parts(grammar_parts)

    out = p_in.split_part(r'\\in', sent)
    print(out)


def test_11():

    '''Test ``split_sent_part`` for term
    ``p_pow`` r"(\))?\^\d"'''
    
    p_pow = PatternRe('pow', r"(\))?\^\d", 'br_right',
                      [False, False, True])

    print('\n test_11: %s' % (p_pow.template))

    grammar_parts = get_tests_grammar_parts()
    p_pow.set_grammar_parts(grammar_parts)

    print("parts:")
    print(p_pow.parts)
    print("map_ptg:")
    print(p_pow.map_ptg)
   
    sent = r'f(n) = n^5 + 4n^2 + 2 |_{n=17}'
    print("sent: %s" % (sent))
    out = p_pow.split_sent_part(r'(\))?\^\d', sent)
    print(out)

    print('\n test_11.1: split_part')
    sent = r'f(n) = n^5 + 4n^2 + 2 |_{n=17}'
    print("sent: %s" % (sent))
    out = p_pow.split_part(r'(\))?\^\d', sent)
    print(out)

    print('\n test_11.2: %s' % (p_pow.template))
    sent = r'^5'
    print("sent: %s" % (sent))
    out = p_pow.split_part(r'(\))?\^\d', sent)
    print(out)
    

def test_12():

    '''Test ``split_sent_part`` for term
    ``p_in`` r"${var}\\in${var}"'''
    
    p_in = PatternRe('in', r"${var}\\in${var}", 'br_mid')
    grammar_parts = get_tests_grammar_parts()
    p_in.set_grammar_parts(grammar_parts)

    print('\n test_12.0: %s' % (p_in.template))
    sent = r'\in'
    print("sent: %s" % (sent))
    out = p_in.split_part(r'\\in', sent)
    print(out)

    print('\n test_12.1: %s' % (p_in.template))
    sent = r''
    
    print("sent: %s" % (sent))
    print("split with '\\in'")
    out = p_in.split_part(r'\\in', sent)
    print(out)


def test_13():

    '''Test ``split_sent_part`` for term
    ``p_cond_all`` r"${var}\\in${var}"
    for sent = "a:b:c \in C"'''

    p_cond_all = PatternRe('cond_all', r"${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])

    grammar_parts = get_tests_grammar_parts()
    p_cond_all.set_grammar_parts(grammar_parts)

    print('\n test_13: %s' % (p_cond_all.template))
    sent = "a:b:c \in C"
    print("sent: %s" % (sent))
    out = p_cond_all.split_part(r':', sent)
    print(out)


def test_14():

    '''Test ``split``
    for term ``p_cond_all``
    r"${{for_all}}${in}:${norm}"'''

    p_cond_all = PatternRe('cond_all', r"\(${{for_all}}${in}:${norm}",
                           'br_left', [True, True, False])
    subterms_values = {'for_all': r"\\for_all"}
    p_cond_all.compile_parts(subterms_values)
    grammar_parts = get_tests_grammar_parts()
    p_cond_all.set_grammar_parts(grammar_parts)
    
    print('\n test_14.0: %s' % (p_cond_all.template))
    sent = ['(\\for_all x \in X: x == y)']
    print("sent: %s" % (str(sent)))
    out = p_cond_all.split(sent)
    print(out)
    
    print('\n test_14.1: %s' % (p_cond_all.template))
    sent = [r'(\for_all x \in X: x == y) and (\for_all y \in Y: y == z)']
    print("sent: %s" % (str(sent)))
    out = p_cond_all.split(sent)
    print(out)


def test_15():
    
    '''Test ``split`` for
    term ``p_func`` and ``p_pow``
    '''
    
    p_func = PatternRe('func', r"${{pred}}\(${args}",
                       'br_left', [True, False, False])
    p_pow = PatternRe('pow', r"${args}\)\^${{float}}",
                      'br_right', [False, False, True])

    '''
    using 'float': r"(?:\d+\.\d+|\d+)"
    (or r"(?:\d+\.\d+|\d+)")
    instead of 'float': r"\d+\.\d+|\d+"
    will prevent re to find only subpattern
    float instead to find all pattern (pow):

    In [58]: re.search(r"\)\^(?:\d+\.\d+|\d+)",'x))^3')
    Out[58]: <_sre.SRE_Match object; span=(2, 5), match=')^3'>

    In [59]: re.search(r"\)\^\d+\.\d+|\d+",'x))^3')
    Out[59]: <_sre.SRE_Match object; span=(4, 5), match='3'>

    '''
    subterms_values = {'pred': r"(?P<obj>\w+)",
                       'float': r"(:\d+\.\d+|\d+)"}

    p_func.compile_parts(subterms_values)
    print("\np_func.value_lex:")
    print(p_func.value_lex)

    p_pow.compile_parts(subterms_values)
    print("\np_pow.value_lex:")
    print(p_pow.value_lex)

    grammar_parts = get_tests_grammar_parts()

    p_func.set_grammar_parts(grammar_parts)
    p_pow.set_grammar_parts(grammar_parts)

    print('\ntest_15:')
    print("\np_pow parts:")
    print(p_pow.parts)
    print("\np_pow map_ptg:")
    print(p_pow.map_ptg)

    sent = [r'(sin(x))^3']
    print("\nsent: %s" % (str(sent)))

    out = p_func.split(sent)
    print("\np_func.split:")
    print(out)

    out = p_pow.split(out)
    print("\np_pow.split:")
    print(out)


def tests_patterns_special():

    print("\n========= FOR: special pattern cases ===========\n")
    test_15()
    print("\n========= END FOR: special pattern cases ===========\n")


def tests_split():

    print("\n======== FOR: pattern split tests =========")
    test_14()
    print("\n======== END FOR: pattern split tests =========")


def tests_split_part():

    print("\n======== FOR: split_sent_part tests =========")
    test_9()
    test_10()
    test_11()
    test_12()
    test_13()
    print("\n======== END FOR: split_sent_part tests =========")


def tests_parts_and_map_ptg():
    print("\n======== FOR: parts and map_ptg tests =========")
    test_7()
    test_8()
    print("\n======== END FOR: parts and map_ptg tests =========")


def tests_base():

    print("\n======== FOR: base tests =========")
    test_0()
    test_1()
    test_2()
    test_3()
    test_3_1()
    test_3_2()
    test_4()
    test_5()
    test_6()
    print("\n======== END FOR: base tests =========")


if __name__ == '__main__':
    
    # test_3_2()
    tests_base()
    tests_parts_and_map_ptg()
    tests_split_part()
    tests_split()
    tests_patterns_special()
