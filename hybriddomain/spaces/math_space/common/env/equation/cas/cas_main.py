import sympy


class CAS():
    def __init__(self, net):
        self.net = net

    def pdsolve(self):

        '''Try to solve pde'''

        Id = sympy.functions.Id
        self.net.eq_sympy_solved = (sympy.pde
                                    .pdsolve(self.net.eq_lambda_sympy_call,
                                             solvefun=Id))
        return(self.net.eq_sympy_solved)

    def plot_pde(self, pde=None):
        '''Try to plot solved pde.
        
        Example:
        >>> e = eq.Equation("U'=-a*(D[U,{x,1}])+U+sin(x)")
        >>> e.parser.parse()
        >>> e.replacer.cpp.editor.set_dim(dim=1)
        >>> e.replacer.sympy.make_sympy()
        >>> e.cas.pdesolve()
        >>> e.cas.plot_pde()
        '''

        # time
        exec("t=sympy.symbols('t')")
        
        # space
        exec("x, y, z = sympy.symbols('x y z')")
        if pde is None:
            sympy.plotting.plot_implicit(self.net.eq_sympy_solved.rhs)
        else:
            sympy.plotting.plot_implicit(pde)

    def classify_pde(self):
        '''
        Example:
        >>> e = Equation("U'=-a*(D[U,{x,1}])+U")
        >>> e.parser.parse()
        >>> e.replacer.cpp.editor.set_dim(dim=1)
        >>> e.replacer.sympy.make_sympy()
        >>> e.cas.classify_pde()
        ('1st_linear_constant_coeff_homogeneous',)
        '''
        return(sympy.classify_pde(self.net.eq_lambda_sympy_call))
