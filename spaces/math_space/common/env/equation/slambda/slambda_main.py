from env.equation.slambda.sympy.slambda_sympy_main import SlambdaSympy

import inspect

import logging

# if using from tester.py uncoment that:
# create logger that child of tests.tester loger
logger = logging.getLogger('equation.slambda')

# if using directly uncoment that:
# create logger
'''
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('equation')
logger.setLevel(level=log_level)
'''


class EqSlambda():

    def __init__(self, net):
        self.net = net
        self.sympy = SlambdaSympy(self)

    def lambdify_call(self, slambda_attr_extractor, tree=None):

        '''
        It used to transfer tree into lambda expresion and
        call it.

        lambda_sem must be used first

        Example:

        >>> e = eq.Equation("sin(0-x)=-sin(x)")
        >>> e.parser.parse()
        >>> e.slambda.sympy.lambdify_sem()
        >>> e.slambda.sympy.lambdify_call()
        True
        '''

        if tree is None:

            # make lambda_sympy and arg_rand
            # for each node
            # self.map_sympy()

            # sample vars:
            # self.get_args()
            # self.sampling()

            tree = self.net.eq_tree_lambda_sympy

        if len(tree) == 0:
            return(slambda_attr_extractor(tree)())
            # return(tree.slambda.sympy())
            
        elif tree.name == 'br':
            # only for one args now:
            func = tree[0]
            args = [self.lambdify_call(slambda_attr_extractor, arg)
                    for arg in tree[1].children]
            # arg = tree[1][0]
            # A = self.lambdify_call(slambda_attr_extractor, arg)
            logger.debug("arg")
            logger.debug(args)

            f = slambda_attr_extractor(func)
            if f is None:
                # if bracket without lambda (like ())
                # return argument:
                # print("args[0]")
                # print(args[0])
                # print(type(args[0]))
                return(args[0])
                # return(A)
            else:
                # print("f source:")
                # print(inspect.getsource(f))
                return(f(*[A for A in args]))
            # if type(A) == str:
            #    A = float(A)
            # return(func.slambda.sympy(A))
            # except AttributeError:
            #    return(self.lambdify_call(slambda_attr_extractor, arg))

        else:
            slambda = slambda_attr_extractor(tree)
            if slambda is None:
                raise(BaseException("fail to extract slambda"
                                    + " for node %s" % (tree)))

            elif len(inspect.getargspec(slambda).args) == 1:
                arg = self.lambdify_call(slambda_attr_extractor, tree[0])
                return(slambda(arg))

            elif len(inspect.getargspec(slambda_attr_extractor(tree)).args) == 2:
                # elif len(inspect.getargspec(tree.slambda.sympy).args) == 2:
                L = self.lambdify_call(slambda_attr_extractor, tree[0])
                # if type(L) == str:
                #     L = float(L)
                R = self.lambdify_call(slambda_attr_extractor, tree[1])
                # if type(R) == str:
                #     R = float(R)

                logger.debug("L, R:")
                logger.debug(L)
                logger.debug(type(L))
                logger.debug(R)
                logger.debug(type(R))
                tree.lambda_args = [L, R]
                return(slambda_attr_extractor(tree)(L, R))
                # return(tree.slambda.sympy(L, R))

    def lambdify(self, slambda_attr_extractor, tree=None):

        '''
        It used to transfer tree, contained lambda
        semantic (created with lambdify_sem),
        into lambda expresion.

        slambda_attr_extractor used to set attribute of node,
        that contained lambda representation of term (created
        with lambdify_sem). Ex: node.slambda.sympy.

        lambda_sem must be used first

        Example:

        >>> e = eq.Equation("sin(0-x)=-sin(x)")
        >>> e.parser.parse()
        >>> e.slambda.sympy.lambdify_sem()
        >>> e.slambda.sympy.lambdify()
        '''

        if tree is None:

            # make lambda_sympy and arg_rand
            # for each node
            # self.map_sympy()

            # sample vars:
            # self.get_args()
            # self.sampling()

            tree = self.net.eq_tree_lambda_sympy

        if len(tree) == 0:
            return(slambda_attr_extractor(tree))
            # return(tree.slambda.sympy)
            # return(lambda: tree.args['variable']['value'])
            
        elif tree.name == 'br':
            # only for one args now:
            func = tree[0]
            args = [self.lambdify(slambda_attr_extractor, arg)
                    for arg in tree[1].children]
            # arg = tree[1][0]
            # A = self.lambdify(slambda_attr_extractor, arg)
            # try:
            logger.debug("args")
            logger.debug(args)
            f = slambda_attr_extractor(func)
            if f is None:
                # if bracket without lambda (like ())
                # return argument:
                return(args[0])
                # return(A)
            else:
                return(lambda: f(*[A() for A in args]))
                # return(lambda: f(A()))
            # return(lambda: func.slambda.sympy(A()))
            # except AttributeError:
            #     return(A)
        else:
            slambda = slambda_attr_extractor(tree)
            if slambda is None:
                raise(BaseException("fail to extract slambda"
                                    + " for node %s" % (tree)))
            elif len(inspect.getargspec(slambda).args) == 1:
                arg = self.lambdify(slambda_attr_extractor, tree[0])
                return(lambda: slambda(arg()))
            elif len(inspect.getargspec(slambda).args) == 2:
                # elif len(inspect.getargspec(tree.slambda.sympy).args) == 2:
                L = self.lambdify(slambda_attr_extractor, tree[0])
                R = self.lambdify(slambda_attr_extractor, tree[1])

                logger.debug("L, R:")
                logger.debug(L)
                logger.debug(type(L))
                logger.debug(R)
                logger.debug(type(R))
                tree.lambda_args = [L, R]
                return(lambda: slambda_attr_extractor(tree)(L(), R()))
                # return(lambda: tree.slambda.sympy(L(), R()))
            
