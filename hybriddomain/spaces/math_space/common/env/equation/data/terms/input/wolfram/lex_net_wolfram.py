from env.equation.data.terms.input.lex_net import LexNet

from env.equation.data.terms.input.wolfram.patterns.base import Base

from env.equation.data.terms.input.wolfram.patterns.arg_int import ArgInt
from env.equation.data.terms.input.wolfram.patterns.arg_float import ArgFloat
from env.equation.data.terms.input.wolfram.patterns.arg_delay import ArgDelay
from env.equation.data.terms.input.wolfram.patterns.arg_time import ArgTime

from env.equation.data.terms.input.wolfram.patterns.var import Var
from env.equation.data.terms.input.wolfram.patterns.var_bdp import VarBdp
from env.equation.data.terms.input.wolfram.patterns.free_var import FreeVar

from env.equation.data.terms.input.wolfram.patterns.coeffs import Coeffs
from env.equation.data.terms.input.wolfram.patterns.bound import Bdp
from env.equation.data.terms.input.wolfram.patterns.diff import Diff
from env.equation.data.terms.input.wolfram.patterns.pow import Pow
from env.equation.data.terms.input.wolfram.patterns.func import Func
from env.equation.data.terms.input.wolfram.patterns.time import Time
from env.equation.data.terms.input.wolfram.patterns.diff_time_var import DiffTimeVar
from env.equation.data.terms.input.wolfram.patterns.dot import Dot
from env.equation.data.terms.input.wolfram.patterns.idx import Idx


class LexNetW(LexNet):

    def get_terms_gen(self):
        
        terms_gens = [Base, ArgInt, ArgFloat, ArgDelay, ArgTime,
                      Var, VarBdp, Coeffs, Bdp, Diff, Pow, Func,
                      FreeVar, Time, DiffTimeVar, Dot, Idx]
        return(terms_gens)

    def get_patterns_order(self):
        
        # order is important for lex:
        patterns_order = ['diff',
                          'bdp',
                          'dot',
                          'func',
                          'idx',
                          'diff_time',
                          'var',
                          'free_var',
                          'time',
                          'coeffs',
                          'pow',
                          'float']
        return(patterns_order)

    def get_map_ptg(self):

        # map patterns to grammar names:
        map_ptg = dict([('diff', 'a'),
                        ('bdp', 'a'),
                        ('diff_time', 'a'),
                        ('var', 'a'),
                        ('free_var', 'a'),
                        ('time', 'a'),
                        ('coeffs', 'a'),
                        ('pow', 'w'),
                        ('func', 'f'),
                        ('float', 'a'),
                        ('dot', 'a'),
                        ('idx', 'i')])
        return(map_ptg)
