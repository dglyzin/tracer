from translator.grammar.grammars import gm_to_cnf
from env.equation.data.grammars.gm_pow_f_args import gm_pow_f_args
from translator.grammar.cyk import cyk

from translator.tokenizer.tokenizer_main import LexNetTokenizer
from env.equation.data.terms.input.wolfram.lex_net_wolfram import LexNetW

from translator.tree.tree_converter import convert
from translator.tree.nodes import NodeCommon


import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('equation.eq_parser')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('eq_parser')
logger.setLevel(level=log_level)



class EqParser():

    def __init__(self, net):
        self.net = net
        
        # FOR lex_nets:
        self.lex_nets = {}

        # patterns (lexems) for wolfram terms:
        self.lex_nets['wolfram'] = LexNetW()
        # END FOR

        # FOR tokenizers:
        self.tokenizers = {}

        # init wolfram tokenizer:
        self.tokenizers['wolfram'] = LexNetTokenizer(self.lex_nets['wolfram'])
        # END FOR
        
        self.tokenizer_current = self.tokenizers['wolfram']

        # lexical analysis of sent:
        self.lex = self.tokenizer_current.lex

    def parse(self):

        '''Parse sent with cyk parser and lexems from lex.

        Input:
        snet - string either like "U'= F" or "F" where
               F must satisfy grammar's rules and lexem's patterns.
        Return:
        operator tree self.eq_tree.
        '''

        # work with prefix:
        self._prefix_step()

        # convert left-midle-right part of eq
        # to tree (for replacer):
        self._convert_to_node()

    def _prefix_step(self):

        '''Transform sent_lex to eq_left, eq_mid, eq_right.
        Where eq_left and eq_right is accepted by cyk parser
        and can be transformed to tree objects,
        eq_mid is either '=' or '=-' or None.

        self.net.sent must exist.
        
        If left brackets would be corrected, it would be
        indicated as:
        self.net._left_brs_added = True

        Example:
        for sent_lex = ["a", "=", "a"]
        return eq_left: (a), eq_mid: '=', eq_right: (a)
        for sent_lex = ["a", "=", "-", "a"]
        return eq_left: (a), eq_mid: '=-',eq_right: (a)
        for sent_lex = ["a", "=", "a", "+", "a"]
        return eq_left: (a), eq_mid: '=', eq_right: a+a
        '''
        sent = self.net.sent

        # remove spaces:
        sent = sent.replace(' ', "")

        # used to indicate that U->(U) for
        # single left term:
        self.net._left_brs_added = False

        mids = ['=-', '=', None]
        for mid in mids:
            if mid is None:
                # if sent is not equation (like U'=sin(U))
                # but just sin(U):
                eq_left = None
                eq_mid = None
                eq_right = self.lex(sent=sent)
                
                # for case a:
                if len(eq_right) == 1:
                    sent_right = "("+sent+")"
                    eq_right = self.lex(sent=sent_right)

                # for case -a or -(a+a):
                elif '-' == eq_right[0]:
                    eq_mid = self.lex(sent='-')
                    
                    # for case -a
                    if len(eq_right[1:]) == 1:
                        sent_right = "("+sent[1:]+")"
                        eq_right = self.lex(sent=sent_right)
                    else:
                        eq_right = eq_right[1:]
            # if sent is equation (U'=sin(U) or U'=-sin(U)
            # or U'=-(U+V)):
            elif mid in sent:
                sent_left, sent_right = sent.split(mid)
                eq_left = self.lex(sent=sent_left)
                eq_mid = self.lex(sent=mid)
                eq_right = self.lex(sent=sent_right)

                # correct left for grammar:
                if len(eq_left) == 1:
                    sent_left = '('+sent_left+')'
                    eq_left = self.lex(sent=sent_left)
                    # print("sent_left")
                    # print(eq_left)
                    # indicate correction for map_out:
                    self.net._left_brs_added = True

                # correct right for grammar:
                if len(eq_right) == 1:
                    sent_right = '('+sent_right+')'
                    eq_right = self.lex(sent=sent_right)
                break

        self.eq = [eq_left, eq_mid, eq_right]

        logger.debug("self.eq:")
        logger.debug(self.eq)

    def _convert_to_node(self):

        '''Get eq_left, eq_mid, eq_right = self.eq
        it convert eq_left and eq_right to
        operator_tree, then convert eq_mid to Node like objects,
        then unite all to single Node like object.'''

        eq_left, eq_mid, eq_right = self.eq
        if eq_left is not None:
            eq_left = self._sym_step(eq_left)
        if eq_right is not None:
            eq_right = self._sym_step(eq_right)
        if eq_mid is not None:
            eq_mid = NodeCommon("".join(eq_mid))

            if (eq_left is not None
                and eq_right is not None):
                # case x=y
                eq_mid.children = [eq_right, eq_left]
            elif eq_left is None:
                # case -y -> 0-y
                eq_left = NodeCommon("0")
                eq_mid.children = [eq_right, eq_left]
            '''
            elif eq_right is None:
                # case y- -> y-0
                # y? -> ?+y
                eq_right = NodeCommon("0")
                eq_mid.children = [eq_right, eq_left]
            '''
            
            if eq_left is None and eq_right is None:
                raise(BaseException("eq_left or eq_right must exist"))

            eq_tree = eq_mid
        else:
            # if equation not like U'=sin(U) but
            # like sin(U)
            eq_tree = eq_right
        
        self.net.eq_tree = eq_tree
            
    def _sym_step(self, goal_sent):

        '''Transform list of Word's into operation's tree
        with grammar'''

        # transform grammar to cnf:
        grammar_cnf = gm_to_cnf(gm_pow_f_args)  # grammar_pow_f

        # parse
        logger.debug("for cyk:")
        logger.debug(goal_sent)
        p, t = cyk(goal=goal_sent, grammar=grammar_cnf)
        self.from_cyk = (p, t)

        # return(t)
        # convert parse tree to operator's tree:
        logger.debug("from_cyk:")
        logger.debug(t)
        ot = convert(t)
        self.operator_tree = ot

        return(ot)

