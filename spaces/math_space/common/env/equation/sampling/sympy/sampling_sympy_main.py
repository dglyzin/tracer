from env.equation.data.terms.rand.sympy.patterns._list import terms_gens as rand_terms_gens


class SamplingSympy():
    
    def __init__(self, net):
        self.net = net
        self.gnet = net.net

    def sampling_subs(self):
        self.net.sampling_subs(rand_terms_gens)

    def sampling_vars(self):
        self.net.sampling_vars(rand_terms_gens)

    def show_sampled(self):
        '''
        Example
        >>> e = Equation("f(a*x+b*y)=a*f(x)+b*f(y)")
        >>> e.parser.parse()
        >>> e.sampling.sympy.sampling_vars()
        >>> # or e.sampling.sympy.sampling_subs()
        >>> e.show_rand()
        sin(0.243*0.570+0.369*0.078)=0.243*sin(0.570)+0.369*sin(0.078)
        '''
        try:
            self.gnet.eq_sympy
        except AttributeError:
            self.gnet.replacer.sympy.make_sympy()
        print(self.gnet.tree.flatten('rand_sympy'))

