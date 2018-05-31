'''
    Algorithm:

    1) lexical analysis:
          U'=c*(D[U,{x,2}+sin(x))]
       to
          a*(a+fa))
       where each a, f is type of Word, and contain original
       lexems in lex arg. (f is short for sin(,cos(,...)
    2) 1 to parse tree (by CYK):
    with grammar:
       E -> E{+-}T|T
       T->T{*/}F|T{*/}W|T{*/}V|F
       W -> (E)^
       V -> f(E)
       F->(E)|a
    (grammar_pow_f from grammars.py)
    to parse tree:
    ('E', ('T', 'T1'))
        child 0: ('T', 'a')
        child 1: ('T1', ('M', 'F'))
           child 0: ('M', '*')
           child 1: ('F', ('L', 'F1'))
              child 0: ('L', '(')
              child 1: ('F1', ('E', 'R'))
                 child 0: ('E', ('E', 'E1'))
                    child 0: ('E', 'a')
                    child 1: ('E1', ('P', 'T'))
                       child 0: ('P', '+')
                       child 1: ('T', ('LF', 'V1'))
                          child 0: ('LF', 'f')
                          child 1: ('V1', ('E', 'RF'))
                             child 0: ('E', 'a')
                             child 1: ('RF', ')')
                 child 1: ('R', ')')
    3) Convert parse tree to operator's tree
    (with convert from trees.py):
       ('M', '*')
            child 0: ('P', '+')
               child 0: ('E', 'a')
                  child 0: ('RF', ')')
                  child 1: ('LF', 'f')
               child 1: ('E', 'a')
               child 2: ('R', ')')
               child 3: ('L', '(')
            child 1: ('T', 'a')

    4) Transform operator's tree to out by replacing lexems
    with func lex_repacer (with convert from op_to_out.py):
    for lex_repacer = lambda x:x[0] result should be same as
    original sent (see op_to_out.py for more):
       
       c*(D[U,{x,2}+sin(x))]

    END OF Algorithm.

'''
from math_space.common.equation.parse.grammars import gm_to_cnf
from math_space.common.equation.parse.grammars import gm_pow_f_args
from math_space.common.equation.tokenizer.lex import lex
from math_space.common.equation.parse.cyk import cyk
from math_space.common.equation.tree.tree_converter import convert
from math_space.common.equation.tree.maps import map_tree, map_tree_postproc
from math_space.common.equation.replacer.cpp.replacer_cpp import CppGen
from math_space.common.equation.replacer.sympy.replacer_sympy import SympyGen
from math_space.common.equation.tree.nodes import NodeCommon

import sys
import inspect
import random

import sympy

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation.py')
logger.setLevel(level=log_level)

logger.debug('sys.path[0]')
logger.debug(sys.path[0])

'''
# add import's path:
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
print(parentdir) 
'''


class Equation():

    def __init__(self, sent, trace=0):
        # remove spaces:
        self.sent = sent.replace(' ', "")

        self.tree_cpp_replacer = CppGen()
        self.sympy_replacer = SympyGen()
        self.prefix = []
        self.operator_tree = None

        # for debugging:
        self.trace = trace

    def convert_to_node(self):

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
        
        self.eq_tree = eq_tree
            
    def _sym_step(self, goal_sent):

        '''Transform list of Word's into operation's tree'''

        # transform grammar to cnf:
        grammar_cnf = gm_to_cnf(gm_pow_f_args)  # grammar_pow_f

        # parse
        logger.debug("for cyk:")
        logger.debug(goal_sent)
        p, t = cyk(goal=goal_sent, grammar=grammar_cnf)
        self.from_cyk = (p, t)

        # return(t)
        # convert parse tree to operator's tree:
        ot = convert(t)
        self.operator_tree = ot

        return(ot)

    def sampling(self):

        '''Generate value for each arg in self.args.
        Used self.args[val].rand_gen for each value. (default is
        set in Equation.get_args)
        If insted of rand_gen has attribute arg_fix, it's value will
        be used instead.
        After that Equation.flatten('rand') can be used to generate
        whole equation.
        Or Equation.lambdify to sample equation.

        Example:
        >>> e = Equation("f(x+y)")
        >>> e.parse()
        >>> e.sampling()
        >>> e.flatten('rand')
        sin(0.2699527968481269+0.6823613609913871+0.2699527968481269)
        >>> e.sampling()
        >>> e.flatten('rand')
        sin(0.7021609513068388+0.9301007659964816+0.7021609513068388)
        '''

        for arg_key in self.args.keys():
            try:
                val = self.args[arg_key].rand_gen()
                for node in self.args[arg_key].nodes:
                    node.rand = val
            except AttributeError:
                # maybe arg has fix value:
                try:
                    val = self.args[arg_key].val_fix
                    for node in self.args[arg_key].nodes:
                        node.rand = val
                except AttributeError:
                    continue

    def get_args(self):

        '''Extract variables from tree.
        For now only work with func_pattern and free_var_pattern

        Example:
        for f(x+y) make self.args for f, x, y.
        They must be alredy recognized by lex.
        it add simple rand_gen to each self.args, that
        used to generate it's values (in self.sampling method).

        It also add sympy_gen attr for vars and constants.
        (for correct call eval(eq) method).

        Example:
        >>> e = Equation('f(x+y+x)+f(x)+g(z)')
        >>> e.parse()
        >>> e.args
        {'f': func_pattern, rand: cos(, nodes count: 2,
         'g': func_pattern, rand: sin(, nodes count: 1,
         'x': free_var_pattern, rand: 0.9204389089496596, nodes count: 3,
         'y': free_var_pattern, rand: 0.08279757240786934, nodes count: 1,
         'z': free_var_pattern, rand: 0.3454996936754938, nodes count: 1}
        '''
        self.args = {}

        class Arg():

            '''Represent arguments of sent with they data.
            f(x+y)-> f, x, y'''

            def __init__(self, name, pattern, node,
                         rand_gen=None, sympy_gen=None, val_fix=None):
                self.name = name
                self.pattern = pattern
                if rand_gen is not None:
                    self.rand_gen = rand_gen
                if sympy_gen is not None:
                    self.sympy_gen = sympy_gen
                if val_fix is not None:
                    self.val_fix = val_fix

                self.nodes = [node]

            def __repr__(self):
                s = "%s, nodes count: %s" % (str(self.pattern),
                                             str(len(self.nodes)))
                try:
                    s = s + " rand: %s" % (str(self.rand_gen()))
                except AttributeError:
                    pass
                try:
                    s = s + " sympy: %s" % (self.sympy_gen)
                except AttributeError:
                    pass
                try:
                    s = s + " val_fix: %s" % (self.val_fix)
                except AttributeError:
                    pass

                return(s)

        for node in self.eq_tree:
            try:
                val, _, pattern = node.name.lex
            except AttributeError:
                continue
            try:
                rand_gen = node.arg_rand
            except AttributeError:
                rand_gen = None
            try:
                sympy_gen = node.arg_sympy
            except AttributeError:
                sympy_gen = None
            try:
                val_fix = node.arg_fix
            except AttributeError:
                val_fix = None

            if (rand_gen is None and sympy_gen is None
                and val_fix is None):
                continue
            if val in self.args.keys():
                self.args[val].nodes.append(node)
            else:
                self.args[val] = Arg(val, pattern, node,
                                     rand_gen, sympy_gen, val_fix)

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
        self.convert_to_node()
    
    def _prefix_step(self):

        '''Transform sent_lex to eq_left, eq_mid, eq_right.
        Where eq_left and eq_right is accepted by cyk parser
        and can be transformed to tree objects,
        eq_mid is either '=' or '=-' or None.

        self.sent must exist.
        
        If left brackets would be corrected, it would be
        indicated as:
        self.left_brs_added = True

        Example:
        for sent_lex = ["a", "=", "a"]
        return eq_left: (a), eq_mid: '=', eq_right: (a)
        for sent_lex = ["a", "=", "-", "a"]
        return eq_left: (a), eq_mid: '=-',eq_right: (a)
        for sent_lex = ["a", "=", "a", "+", "a"]
        return eq_left: (a), eq_mid: '=', eq_right: a+a
        '''
        sent = self.sent

        # remove spaces:
        sent = sent.replace(' ', "")

        # used to indicate that U->(U) for
        # single left term:
        self.left_brs_added = False

        mids = ['=-', '=', None]
        for mid in mids:
            if mid is None:
                # if sent is not equation (like U'=sin(U))
                # but just sin(U):
                eq_left = None
                eq_mid = None
                eq_right = lex(sent=sent)
                
                # for case a:
                if len(eq_right) == 1:
                    sent_right = "("+sent+")"
                    eq_right = lex(sent=sent_right)

                # for case -a or -(a+a):
                elif '-' == eq_right[0]:
                    eq_mid = lex(sent='-')
                    
                    # for case -a
                    if len(eq_right[1:]) == 1:
                        sent_right = "("+sent[1:]+")"
                        eq_right = lex(sent=sent_right)
                    else:
                        eq_right = eq_right[1:]
            # if sent is equation (U'=sin(U) or U'=-sin(U)
            # or U'=-(U+V)):
            elif mid in sent:
                sent_left, sent_right = sent.split(mid)
                eq_left = lex(sent=sent_left)
                eq_mid = lex(sent=mid)
                eq_right = lex(sent=sent_right)

                # correct left for grammar:
                if len(eq_left) == 1:
                    sent_left = '('+sent_left+')'
                    eq_left = lex(sent=sent_left)

                    # indicate correction for map_out:
                    self.left_brs_added = True

                # correct right for grammar:
                if len(eq_right) == 1:
                    sent_right = '('+sent_right+')'
                    eq_right = lex(sent=sent_right)
                break
        
        self.eq = [eq_left, eq_mid, eq_right]

    def map_out(self, replacer):

        '''Add out to self.eq_tree (from self.parse)'''

        _map = map_tree(self.eq_tree, replacer)
        _map_postproc = map_tree_postproc(_map, replacer)

        # if brackets was added to left part of equation
        # like U'= -> (U')=
        # then remove them:
        # from '='->[br-> ['(', args->[a], ')'], right]
        # to '='-> [a, right]:
        if self.left_brs_added:
            br_child = _map_postproc.children[1]
            child = br_child.children[1].children[0]
            _map_postproc.replace_child(br_child, child)
            self.left_brs_added = False

        return(_map_postproc)

    def map_cpp(self):
        return(self.map_out(self.tree_cpp_replacer))

    def map_sympy(self):
        return(self.map_out(self.sympy_replacer))

    def flatten(self, key):

        '''Return list of term as key.
        Key either original or cpp.'''
        
        if key == 'cpp':
            kernel = self.map_cpp()
        elif key == 'original':
            kernel = self.eq_tree
        elif key == 'rand':
            kernel = self.eq_tree
        elif key == 'sympy':
            kernel = self.map_sympy()

        logger.debug("kernel")
        logger.debug(kernel)

        out_kernel = kernel.flatten(key)
            
        return("".join(out_kernel))

    def lambdify_call(self, tree=None):

        '''
        It used to transfer tree into lambda expresion and
        call it.

        map_sympy, get_args and sampling must be used first

        Example:

        >>> e = eq.Equation("sin(0-x)=-sin(x)")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.sampling()
        >>> e.lambdify()
        True
        '''

        if tree is None:

            # make lambda_sympy and arg_rand
            # for each node
            # self.map_sympy()

            # sample vars:
            # self.get_args()
            # self.sampling()

            tree = self.eq_tree

        if len(tree) == 0:
            return(tree.rand)
            
        elif tree.name == 'br':
            # only for one args now:
            func = tree[0]
            arg = tree[1][0]
            try:
                A = self.lambdify_call(arg)
                # if type(A) == str:
                #    A = float(A)
                logger.debug("arg")
                logger.debug(A)
                logger.debug(type(A))
                return(func.lambda_sympy(A))
            except AttributeError:
                return(self.lambdify_call(arg))

        elif len(inspect.getargspec(tree.lambda_sympy).args) == 2:
            L = self.lambdify_call(tree[0])
            # if type(L) == str:
            #     L = float(L)
            R = self.lambdify_call(tree[1])
            # if type(R) == str:
            #     R = float(R)

            logger.debug("L, R:")
            logger.debug(L)
            logger.debug(type(L))
            logger.debug(R)
            logger.debug(type(R))
            tree.lambda_args = [L, R]
            return(tree.lambda_sympy(L, R))

    def lambdify(self, tree=None):

        '''
        It used to transfer tree into lambda expresion.

        Only for float now

        map_sympy, get_args and sampling must be used first

        Example:

        >>> e = eq.Equation("sin(0-x)=-sin(x)")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.sampling()
        >>> e.lambdify()
        '''

        if tree is None:

            # make lambda_sympy and arg_rand
            # for each node
            # self.map_sympy()

            # sample vars:
            # self.get_args()
            # self.sampling()

            tree = self.eq_tree

        if len(tree) == 0:
            
            return(lambda: tree.rand)
            
        elif tree.name == 'br':
            # only for one args now:
            func = tree[0]
            arg = tree[1][0]
            try:
                A = self.lambdify(arg)
                logger.debug("arg")
                logger.debug(A)
                logger.debug(type(A))
                return(lambda: func.lambda_sympy(A()))
            except AttributeError:
                return(self.lambdify(arg))

        elif len(inspect.getargspec(tree.lambda_sympy).args) == 2:
            L = self.lambdify(tree[0])
            R = self.lambdify(tree[1])

            logger.debug("L, R:")
            logger.debug(L)
            logger.debug(type(L))
            logger.debug(R)
            logger.debug(type(R))
            tree.lambda_args = [L, R]
            return(lambda: tree.lambda_sympy(L(), R()))
            
    def make_sympy(self):

        '''Make sympy equation.

        Example:
        >>> e = Equation("U'=-a*(D[U,{x,1}])+U")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.eq_sympy
        Eq(Derivative(U(t, x), t), U(t, x) - 0.014*Derivative(U(t, x), x))
        '''
        eq_sympy = self.flatten('sympy')
        logger.debug("eq_sympy")
        logger.debug(eq_sympy)
        
        # extract vars for sampling:
        self.get_args()

        # fill some attributes:
        self.sampling()

        # generate var (U) and const (a):
        for karg in self.args.keys():
            try:
                if self.args[karg].sympy_gen is not None:

                    var = str(self.args[karg].sympy_gen)
                    
                    logger.debug("sympy_gen:")
                    logger.debug(var)

                    # add vars to current state:
                    try:
                        exec("%s = sympy.simplify('%s')" % (var, var))
                    except:
                        exec("%s = sympy.simplify('%s')" % (karg, var))
            except AttributeError:
                continue

        # time
        exec("t=sympy.symbols('t')")

        # space
        exec("x, y, z = sympy.symbols('x y z')")

        eq_left, eq_right = eq_sympy.split('=')
        self.eq_sympy = eval("sympy.Eq(%s, %s)" % (eq_left, eq_right))
        # self.eq_sympy = sympy.sympify("Eq(%s, %s)" % (eq_left, eq_right))
        sympy.printing.pprint(self.eq_sympy)

    def pdsolve(self):

        '''Try to solve pde'''

        Id = sympy.functions.Id
        self.eq_sympy_solved = sympy.pde.pdsolve(self.eq_sympy, solvefun=Id)
        return(self.eq_sympy_solved)

    def plot_pde(self):
        '''Try to plot solved pde.
        
        Example:
        >>> e = eq.Equation("U'=-a*(D[U,{x,1}])+U+sin(x)")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.pdesolve()
        >>> e.plot_pde()
        '''

        # time
        exec("t=sympy.symbols('t')")
        
        # space
        exec("x, y, z = sympy.symbols('x y z')")
        sympy.plotting.plot_implicit(self.eq_sympy_solved.rhs)
        
    def show_original(self):
        print(self.flatten("original"))

    def show_cpp(self):
        print(self.flatten('cpp'))

    def show_rand(self):
        '''
        Example
        >>> e = Equation("f(a*x+b*y)=a*f(x)+b*f(y)")
        >>> e.parse()
        >>> e.sampling()
        >>> e.show_rand()
        sin(0.243*0.570+0.369*0.078)=0.243*sin(0.570)+0.369*sin(0.078)
        '''
        print(self.flatten('rand'))
    
    def show_sympy(self):
        '''
        Example:
        >>> e = Equation("U'=-a*(D[U,{x,1}])+U")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.show_sympy()
        '''
        print(sympy.printing.pprint(self.eq_sympy))

    def __repr__(self):
        out = self.sent
        return(out)

    def classify_pde(self):
        '''
        Example:
        >>> e = Equation("U'=-a*(D[U,{x,1}])+U")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.classify_pde()
        ('1st_linear_constant_coeff_homogeneous',)
        '''
        return(sympy.classify_pde(self.eq_sympy))

    def show_tree_original(self):
        print(self.eq_tree.show_original())
    
    def show_tree_cpp_out(self):
        print(self.eq_tree.show_cpp_out())
        
    def show_tree_cpp_data(self):
        print(self.eq_tree.show_cpp_data())

    def show_tree_sympy(self):
        print(self.eq_tree.show_sympy_out())
    
    # FOR set out cpp parameters:

    def set_default(self):
        self.set_dim(dim=2)
        self.set_blockNumber(blockNumber=0)

        self.set_vars_indexes(vars_to_indexes=[('U', 0), ('V', 1)])

        coeffs_to_indexes = [('a', 0), ('b', 1), ('c', 2), ('r', 3)]
        self.set_coeffs_indexes(coeffs_to_indexes=coeffs_to_indexes)

        self.set_diff_type(diffType='pure',
                           diffMethod='common')
        self.set_shape(shape=[30, 30])

    def set_dim(self, **kwargs):

        '''dim=2'''

        self.tree_cpp_replacer.set_dim(**kwargs)
        self.sympy_replacer.set_dim(**kwargs)

    def set_blockNumber(self, **kwargs):
        '''blockNumber=0'''
        self.tree_cpp_replacer.set_blockNumber(**kwargs)

    def set_vars_indexes(self, **kwargs):

        ''' Shift index for variable:
        like (U,V)-> (source[+0], source[+1])

        Input:
        vars_to_indexes=[('U', 0), ('V', 1)]
        '''

        self.tree_cpp_replacer.set_vars_indexes(**kwargs)
        
    def set_diff_type(self, **kwargs):

        '''
        Inputs:
           diffType="pure", diffMethod="common"

           diffType="pure", diffMethod="special",
           side=0, func="sin(x)"

           diffType="pure", diffMethod="interconnect",
           side=0, firstIndex=0, secondIndexSTR=1
        '''

        self.tree_cpp_replacer.set_diff_type(**kwargs)

    def set_shape(self, **kwargs):

        '''For bound like "V(t-1.1,{x,1.3}{y, 5.3})".

        Input:
        shape=[3, 3]'''

        self.tree_cpp_replacer.set_shape(**kwargs)
        
    def set_coeffs_indexes(self, **kwargs):

        '''map coeffs ot it's index
        like (a,b)-> (params[+0], params[+1])

        Input:
        coeffs_to_indexes=[('a', 0), ('b', 1)]
        '''
        self.tree_cpp_replacer.set_coeffs_indexes(**kwargs)

    # END FOR
