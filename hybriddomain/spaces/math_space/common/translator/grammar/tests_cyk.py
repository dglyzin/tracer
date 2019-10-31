# parser$ python3 -m translator.grammar.tests_cyk
# from translator.grammar.grammars import gm_to_cnf
# from env.equation.data.grammars.gm_pow_f_args import gm_pow_f_args
from translator.grammar.cyk import cyk
from translator.grammar.cyk import preproc as preproc_cyk
from translator.grammar.grammars import get_fmw

from translator.tree.tree_converter import convert
# from translator.tree.nodes import NodeCommon

from translator.tokenizer.tokenizer_main import TokenizerNet
from translator.tokenizer.patterns.patterns_list.tests.dialects import cs, eqs

from translator.tokenizer.tests.tests_list import tests_dict_eqs
from translator.tokenizer.tests.tests_list import tests_dict_cs

import os
import sys
import inspect
import traceback

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.gen_1d')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('tests_map')
logger.setLevel(level=log_level)

# insert env dir into sys
# env must contain env folder:
currentdir = os.path.dirname(os.path
                             .abspath(inspect.getfile(inspect.currentframe())))
env = currentdir.find("env")
env_dir = currentdir[:env]
logger.debug(env_dir)
if env_dir not in sys.path:
    sys.path.insert(0, env_dir)


def make_tokenizer(dialect):
    tokenizer = TokenizerNet()
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
    tokenizer.set_grammar_parts(grammar_parts)
    tokenizer.load_patterns(dialect)

    return(tokenizer)


def test_all_eqs():
    dialect = "eqs"
    test_all(dialect, tests_dict_eqs)


def test_all_cs():
    dialect = "cs"
    test_all(dialect, tests_dict_cs)


def test_all(dialect, tests_list):
    if dialect == "cs":
        tokenizer = make_tokenizer(cs)
    elif dialect == "eqs":
        tokenizer = make_tokenizer(eqs)

    succesed = []
    failed = []

    for _id in tests_list:
        if test_one(tokenizer, tests_list, dialect=dialect, _id=_id):
            succesed.append(_id)
        else:
            failed.append(_id)

    print("\ntests failed %s from %s:"
          % (len(failed), len(failed)+len(succesed)))
    print(failed)

    
def test_one(tokenizer, tests_list, dialect="eqs", _id=0, verbose=False):
    
    sent_list = tests_list[_id]
    sent_list = [sent.replace(" ", "")
                 for sent in sent_list]
    print("\n=== test %s: %s ===" % (_id, sent_list))
    out = tokenizer.lex(sent_list)

    out = preproc_cyk(out)
    # out = sum([list(o) for o in out], [])

    if verbose:
        print("out_lex:")
        print(out)

    # transform grammar to cnf:
    if dialect == "eqs":
        grammar_fmw = get_fmw()
    elif dialect == "cs":
        grammar_fmw = get_fmw(ms=[["clause_where", "clause_for",
                                   "clause_into"],
                                  "def_0", "in_0",
                                  ["if", "if_only", "if_def"],
                                  "clause_or", "conj"])

    # choice ops for dialect:
    if dialect == "eqs":
        node_data = {"ops": ['add', 'sub', 'mul', 'div', 'eq', ]}
        
    elif dialect == "cs":
        node_data = {"ops": ["clause_where", "clause_for", "clause_into",
                             "def_0", "in_0",
                             "if", "if_only", "if_def",
                             "clause_or", "conj"]}

    if verbose:
        print("grammar_fmw:")
        for rule in grammar_fmw:
            print(rule)
    
    try:
        # parse
        p, t = cyk(goal=out, grammar=grammar_fmw,
                   node_data=node_data)
        if type(p) == dict:
            print("fail test %s" % (_id))
            if verbose:
                print("result trees:")
                print(t)
            return(False)

    except BaseException as e:
        print("fail test %s" % (_id))
        if verbose:
            print(e)
            traceback.print_exc()
        return(False)
    
    # print("p:")
    # print(p)
    if verbose:
        print("t:")
        print(t)

    try:
        # convert parse tree to operator's tree:
        ot = convert(t)
        
    except BaseException as e:
        print("fail test %s" % (_id))
        if verbose:
            print(e)
            traceback.print_exc()
        return(False)
    if verbose:
        print("ot:")
        print(ot.__repr__(node_attr_to_show="name"))
    return(ot)
    '''
    if not verbose:
        return(True)
    else:
        return(ot)
    '''


if __name__ == '__main__':

    # test_all_cs()
    # test_all_eqs()
    tokenizer = make_tokenizer(eqs)
    tests_list = tests_dict_eqs
    dialect = "eqs"
    test_one(tokenizer, tests_list, dialect=dialect, _id=17, verbose=True)
