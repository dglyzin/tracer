'''
parser$ python3 -m translator.tokenizer.patterns.patterns_list.tests.tests_patterns_list

'''
from translator.tokenizer.patterns.patterns_list.patterns_list_main import Patterns
from translator.tokenizer.patterns.patterns_list.tests.dialects import cs, eqs


def test_make(dialect):
    
    patterns = Patterns()
    grammar_parts = {'a': 'a',
                     'br': {'br_left':
                            {'left': 'f',
                             'mid': ',',
                             'right': ')'},
                            'br_mid':
                            {'mid': 'm'},
                            'br_right':
                            {'left': '(',
                             'mid': ',',
                             'right': 'w'}}}
    patterns.make_patterns(dialect)
    patterns.compile_patterns(grammar_parts)
    return(patterns)


def test_orders():
    dialect = cs
    patterns = test_make(dialect)
    
    print("\n========= tests orders ===========\n")
    
    print("\ntest_0.0: let < def_0")
    pattern_0 = patterns.patterns_dict_objs['let']
    pattern_1 = patterns.patterns_dict_objs['def_0']

    # p0 < p1
    out = patterns.sorter.choice_order(pattern_0, pattern_1)
    print("\ntest_0.0 result:")
    print(out)

    print("\ntest_0.1: def_0 < let")
    pattern_0 = patterns.patterns_dict_objs['let']
    pattern_1 = patterns.patterns_dict_objs['def_0']

    # p0 < p1
    out = patterns.sorter.choice_order(pattern_1, pattern_0)
    print("\ntest_0.1 result:")
    print(out)

    print("\ntest_1.0: var < set")
    pattern_0 = patterns.patterns_dict_objs['var']
    pattern_1 = patterns.patterns_dict_objs['set']

    # p0 < p1
    out = patterns.sorter.choice_order(pattern_0, pattern_1)
    print("\ntest_1.0 result:")
    print(out)

    print("\ntest_1.1: set < var")
    pattern_0 = patterns.patterns_dict_objs['var']
    pattern_1 = patterns.patterns_dict_objs['set']

    # p0 < p1
    out = patterns.sorter.choice_order(pattern_1, pattern_0)
    print("\ntest_1.1 result:")
    print(out)


def test_sort(dialect):
    patterns = test_make(dialect)
    print("\n========= tests sort ===========\n")
    
    print("\ntest_0.0: cs")
    
    sorted = patterns.sorter.sort()
    sorted_terms_names = [el[0] for el in sorted]
    print("\nsorted_terms_names:")
    print(sorted_terms_names)


if __name__ == '__main__':
    
    test_sort(eqs)
    # test_sort(cs)
    # test_orders()
    # test_make(eqs)
    # test_make(cs)
