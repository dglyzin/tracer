'''
Tests list of tests from

   ``parser/translator/tokenizer/tests/tests_list``

- ``use_asserted`` -- if True checks with ``*_asserted`` list

Command::

   parser$ python3 -m translator.tokenizer.tests.tests_tokenizer_main

'''
from translator.tokenizer.tokenizer_main import TokenizerNet
from translator.tokenizer.patterns.patterns_list.tests.dialects import cs, eqs
from translator.tokenizer.tests.tests_list import tests_dict_cs
from translator.tokenizer.tests.tests_list import cs_asserted
from translator.tokenizer.tests.tests_list import tests_dict_eqs
from translator.tokenizer.tests.tests_list import eqs_asserted

from translator.grammar.cyk_1 import preproc as preproc_cyk


def make_tokenizer(dialect):
    tokenizer = TokenizerNet()
    grammar_parts = {'a': 'a',
                     'br': {'br_left':
                            {'left': 'f(',
                             'mid': ',',
                             'right': ')'},
                            'br_mid':
                            {'mid': 'm'},
                            'br_right':
                            {'left': '(',
                             'mid': ',',
                             'right': ')w'}}}
    tokenizer.set_grammar_parts(grammar_parts)
    tokenizer.load_patterns(dialect)

    # print("tokenizer.patterns_list_sorted:")
    # print(tokenizer.patterns_list_sorted)
    return(tokenizer)


def test_cs(use_asserted):
    
    tokenizer = make_tokenizer(cs)

    failed = []

    if (len(tests_dict_cs) != len(cs_asserted)
        and use_asserted):
        msg = ("\nlens of tests_list_cs and cs_asserted"
               + " must be same"
               + "\nso add needed results for tests_list_cs"
               + " in cs_asserted list"
               + "\nor use_asserted = False")

        raise(BaseException(msg))

    for i in tests_dict_cs:
        sent_list = tests_dict_cs[i]

        print("\nsent_list:")
        print(sent_list)

        sent_list = [sent.replace(" ", "")
                     for sent in sent_list]
        out = tokenizer.lex(sent_list)

        out = preproc_cyk(out)

        print("\n out:")
        print(out)

        if use_asserted:
            # FOR check correctness:
            asserted = (out == cs_asserted[i])
            print("\n out == asserted")
            print(asserted)
            if not asserted:
                failed.append((i, sent_list, out, cs_asserted[i]))
            # END FOR

        '''
        print("\nwords:")
        for word in out:
            try:
                word.lex
                print("\nword:")
                print(word)
                print(word.lex['term_name'])
            except AttributeError:
                continue
        '''
    return(failed)

    
def test_eqs(use_asserted):
    
    tokenizer = make_tokenizer(eqs)
    
    failed = []

    if (len(tests_dict_eqs) != len(eqs_asserted)
        and use_asserted):
        msg = ("\nlens of tests_list_eqs and eqs_asserted"
               + " must be same"
               + "\nso add needed results for tests_list_eqs"
               + " in eqs_asserted list"
               + "\nor use_asserted = False")

        raise(BaseException(msg))

    print("\npatterns templates:")
    templates = [(entry[0], entry[1].template)
                 for entry in tokenizer.patterns_list_sorted]
    for entry in templates:
        print(entry[0]+": "+entry[1])

    for i in tests_dict_eqs:
        sent_list = tests_dict_eqs[i]

        print("\nsent_list:")
        print(sent_list)

        sent_list = [sent.replace(" ", "")
                     for sent in sent_list]

        out = tokenizer.lex(sent_list)

        out = preproc_cyk(out)

        print("\n out:")
        print(out)

        if use_asserted:
            # FOR check correctness:
            asserted = (out == eqs_asserted[i])
            print("\n out == asserted")
            print(asserted)
            if not asserted:
                failed.append((i, sent_list, out, eqs_asserted[i]))
            # END FOR
    
        '''
        print("\nwords:")
        for word in out:
            try:
                word.lex
                print("\nword:")
                print(word)
                print(word.lex['term_name'])
            except AttributeError:
                continue
        '''
    return(failed)


if __name__ == "__main__":
    
    # make_tokenizer(cs)
    # faileds = test_cs(True)
    faileds = test_eqs(True)

    for failed in faileds:
        print("\n fail:")
        print(failed)

