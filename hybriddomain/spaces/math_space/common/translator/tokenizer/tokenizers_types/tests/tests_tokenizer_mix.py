# parser$ python3 -m translator.tokenizer.tokenizers_types.tests.tests_tokenizer_mix
from translator.tokenizer.tokenizers_types.tokenizer_mix import LexMixTokenizer
from translator.tokenizer.patterns.patterns_types.pattern_re import PatternRe
from translator.tokenizer.patterns.patterns_types.pattern_txt import PatternTxt


if __name__ == '__main__':

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

    print('\n test_0: br terms')

    p_in = PatternRe('in', r"${var}\\in${var}", 'br_mid')
    p_norm = PatternRe('norm', r"${var}\\norm${var}", 'br_mid')
    p_cond_all = PatternRe('cond_all', r"\\for_all${in}:${norm}",
                           'br_left', [True, True, False])
    
    patterns = [p_in, p_norm, p_cond_all]

    for pattern in patterns:
        pattern.set_grammar_parts(grammar_parts)

    tok = LexMixTokenizer()
    tok.set_patterns_list(patterns)

    sent = ['\\for_all x \in X: x(t-1.0) == y(t-1.1)',
            ' and \\for_all y \in Y: y(t-1.1) == z(t-1.2)']
    print("sent:")
    print(sent)

    out = tok.lex_br(sent)
    print(out)

    print('\ntest_1: a terms')

    p_float = PatternRe('float', r"\d+\.\d+|\d+", 'a')
    p_arg_delay = PatternRe('arg_delay', r"(?P<delay>${{float}})",
                            'a')
    p_arg_time = PatternRe('arg_time', r"[t](-${{arg_delay}})?",
                           'a')
    subterms_values = {'arg_delay': p_arg_delay.template,
                       'float': p_float.template}
    p_arg_time.compile_parts(subterms_values)
    print("\nvalue_lex")
    print(p_arg_time.value_lex)

    patterns = [p_arg_time]

    for pattern in patterns:
        pattern.set_grammar_parts(grammar_parts)

    tok = LexMixTokenizer()
    tok.set_patterns_list(patterns)
    out = tok.lex_br(sent)
    print(out)

    print("\nfound WordDict re_res:")
    for elm in out:
        if type(elm) != str:
            print(elm.lex['re_res'])
    
    print('\ntest_2: br terms txt')

    sent = ['\\for_all x \in X: x(t-1.0) == y(t-1.1)',
            ' and \\for_all y \in Y: y(t-1.1) == z(t-1.2)']
   
    p_in = PatternTxt('in', r"${var}\in${var}", 'br_mid')
    p_norm = PatternTxt('norm', r"${var}\norm${var}", 'br_mid')
    p_cond_all = PatternTxt('cond_all', r"\for_all${in}:${norm}",
                            'br_left', [True, True, False])
    
    patterns = [p_in, p_norm, p_cond_all]

    for pattern in patterns:
        pattern.set_grammar_parts(grammar_parts)

    tok = LexMixTokenizer()
    tok.set_patterns_list(patterns)
    sent = ['\\for_all x \in X: x(t-1.0) == y',
            ' and \\for_all y \in Y: y == z']
    print("sent:")
    print(sent)

    out = tok.lex_br(sent)
    print(out)

    print('\ntest_3: a terms txt')
    # wery artificial example
    # a txt term not suppose to be used much
    p_float = PatternTxt('float', r"1.0", 'a')
    p_arg_delay = PatternTxt('arg_delay', r"${{float}}",
                             'a')
    p_arg_time = PatternTxt('arg_time', r"t-${{arg_delay}}",
                            'a')
    subterms_values = {'arg_delay': p_arg_delay.template,
                       'float': p_float.template}
    p_arg_time.compile_parts(subterms_values)
    print("\nvalue_lex")
    print(p_arg_time.value_lex)

    patterns = [p_arg_time]

    for pattern in patterns:
        pattern.set_grammar_parts(grammar_parts)

    tok = LexMixTokenizer()
    tok.set_patterns_list(patterns)
    out = tok.lex_br(sent)
    print(out)
