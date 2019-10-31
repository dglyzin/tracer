from env.equation.data.terms.output.sympy.replacer_sympy import SympyGen
import sympy


class ReplSympy():
    
    '''Convert tree's nodes to cpp'''
    
    def __init__(self, net):
        self.net = net
        self.gen = SympyGen()

    def map_sympy(self):
        return(self.net.tree.map_out(self.gen))
        
    def make_sympy(self):
        self.map_sympy()
        self.net.eq_sympy = self.net.tree.flatten('sympy')
        return(self.net.eq_sympy)

    def show_sympy(self):
        '''
        Example:
        >>> e = Equation("U'=-a*(D[U,{x,1}])+U")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.show_sympy()
        '''
        sympy.printing.pprint(self.net.eq_sympy)

    def show_tree_sympy(self):
        print(self.net.eq_tree.show_sympy_out())
    

    '''
        def make_sympy(self):

        ''Make sympy equation.

        Example:
        >>> e = Equation("U'=-a*(D[U,{x,1}])+U")
        >>> e.parse()
        >>> e.set_dim(dim=1)
        >>> e.make_sympy()
        >>> e.eq_sympy
        Eq(Derivative(U(t, x), t), U(t, x) - 0.014*Derivative(U(t, x), x))
        ''
        eq_sympy = self.tree.flatten('sympy')
        logger.debug("eq_sympy")
        logger.debug(eq_sympy)
        for term in eq_sympy:
            try:
                logger.debug(term.sympy)
            except:
                pass
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
        
        # for U' = sin(x)
        # try:
        eq_left, eq_right = eq_sympy.split('=')
        self.eq_sympy = eval("sympy.Eq(%s, %s)" % (eq_left, eq_right))
        # self.eq_sympy = sympy.sympify("Eq(%s, %s)" % (eq_left, eq_right))
        # except ValueError:
        #    for sin(x):
        #    self.eq_sympy = eval("sympy.Eq(%s)" % (eq_sympy))

        sympy.printing.pprint(self.eq_sympy)

    '''
