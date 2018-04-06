from replacer.cpp.additions.deriv import PureDerivGenerator
from replacer.cpp.additions.deriv import MixDerivGenerator

import logging

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('cpp_out.py')
logger.setLevel(level=log_level)


class Params():
    def __init__(self):
        self.diffType = None  # 'pure'
        self.diffMethod = None  # 'vertex'

        # int: shift index for variable like
        # like (U,V)-> (source[+0], source[+1])
        self.unknownVarIndexes = []

        # {x, 2}
        self.indepVarList = []
        self.indepVarOrders = {}
        self.derivOrder = None

        self.blockNumber = None
        self.side = None


class Term():

    '''Common methods for all cpp terms'''

    def __init__(self, parent):

        # for debugging:
        self.dbg = True
        self.dbgInx = 4

        self.parent = parent
        self.params = Params()

    def set_dim(self, dim):
        self.params.dim = dim

    def set_blockNumber(self, blockNumber):
        self.params.blockNumber = blockNumber

    def set_var_index(self, term):
        var = term.name.lex[1].group('val')
        # for case like U(t-1.1)
        var = var[0]
        self.params.unknownVarIndex = self.params.map_vti[var]

    def set_vars_indexes(self, map_vti):
        # int: shift index for variable like
        # like (U,V)-> (source[+0], source[+1])

        self.params.map_vti = map_vti

    def set_delay(self, term):

        '''Find values and it's delay (like (t-1.1))
        and add term index to global_params
        (for conversion in postprocessing)'''

        pattern = term.name.lex[1]

        delay = pattern.group('delay')
        if delay is not None:
            self.parent.global_params.delays_owner_id += 1
            delay_index = self.parent.global_params.delays_owner_id
            self.parent.global_params.delays[delay_index] = delay
            val_index = pattern.group('val')
            return((delay_index, val_index, delay))
        return(None)

    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                print(self.dbgInx*' '+str(arg))
            print('')


class Diff(Term):

    def set_base(self, term):

        '''Used for fill local data'''

        '''Orders and varList will be set here
        from term's pattern (like {x, 2})
        Return delay data.
        '''

        self.set_varList(term)
        self.set_var_index(term)
        delay_data = self.set_delay(term)

        # add delays data for postproc:
        if delay_data is not None:
            return({'delay_data': delay_data})
        else:
            return(None)

    def set_varList(self, term):

        '''Find values and it's orders (like {x, 2})'''
        
        pattern = term.name.lex[1]
        for var in 'xyz':
            order = pattern.group('val_'+var)
            if order is not None:
                self.params.indepVarList.append(var)
                self.params.indepVarOrders[var] = int(order)
                break

    def set_diff_type(self, **kwargs):

        '''
        Inputs:
           diffType="pure", diffMethod="common"

           diffType="pure", diffMethod="special",
           side=0, func="sin(x)"

           diffType="pure", diffMethod="interconnect",
           side=0, firstIndex=0, secondIndexSTR=1
        '''

        self.params.diffType = kwargs['diffType']
        self.params.diffMethod = kwargs['diffMethod']
        diffMethod = self.params.diffMethod
        if diffMethod == 'special':
            try:
                self.params.side = kwargs['side']
                self.params.func = kwargs['func']
            except:
                raise(BaseException(('for method special side'
                                     + ' and func must be given')))
        elif diffMethod == 'interconnect':
            try:
                self.params.side = kwargs['side']
                self.params.firstIndex = kwargs['firstIndex']
                self.params.secondIndexSTR = kwargs['secondIndexSTR']
            except:
                raise(BaseException(('for method interconnect'
                                     + ' side, firstIndex and secondIndexSTR'
                                     + ' must be given')))
        elif diffMethod == 'vertex':
            try:
                self.params.vertex_sides = kwargs['vertex_sides']
            except:
                raise(BaseException(('for method vertex vertex_sides'
                                     + 'must be given')))

    def print_cpp(self):
        '''
        global_params = {
            # int: shift index for variable like
            # like (U,V)-> (source[+0], source[+1])
            'unknownVarIndex': 0
                
            'blockNumber': 0
            'side': 0

            'diffType': 'pure'
            'diffMethod': 'vertex'}
        '''
        return(self.diff())

    def diff(self):
        '''
        DESCRIPTION:
        self.params should be initiated first.
        '''
        logger.debug("FROM diff:")
        if (self.params.diffMethod is None
            or self.params.diffType is None):
            raise(BaseException('set_diff_type first'))
        if self.params.diffType == 'pure':
            if self.params.diffMethod == 'common':
                return(self.diff_pure_common())
            if self.params.diffMethod == 'special':
                return(self.diff_pure_spec())
            if self.params.diffMethod == 'interconnect':
                return(self.diff_pure_ics())
            if self.params.diffMethod == 'vertex':
                return(self.diff_pure_vertex())

    def diff_pure_common(self):
        # for debug
        logger.debug("diffType: pure, common")
        diffGen = PureDerivGenerator(self.params)
        out = diffGen.common_diff()
        return(out)

    def diff_pure_spec(self):
        # for debug
        logger.debug("diffType: pure, spec")
        diffGen = PureDerivGenerator(self.params)
        func = self.params.func
        out = diffGen.special_diff(func)
        return(out)

    def diff_pure_ics(self):
        # for debug
        logger.debug("diffType: pure, interconnect")
        diffGen = PureDerivGenerator(self.params)
        out = diffGen.interconnect_diff()
        return(out)

    def diff_pure_vertex(self):
        logger.debug("vertex not implemented")
        return(None)

    def diff_mix_common(self):
        # for debug
        logger.debug("diffType: pure, common")
        diffGen = MixDerivGenerator(self.params)
        out = diffGen.common_diff()
        return(out)

    def diff_mix_spec(self):
        # for debug
        logger.debug("diffType: pure, spec")
        diffGen = MixDerivGenerator(self.params)
        func = self.params.func
        out = diffGen.special_diff(func)
        return(out)

    def diff_mix_ics(self):
        # for debug
        logger.debug("diffType: pure, interconnect")
        diffGen = MixDerivGenerator(self.params)
        out = diffGen.interconnect_diff()
        return(out)

    def diff_none(self):
        # for debug
        logger.debug("diffMethod: None")
        diffGen = PureDerivGenerator(self.params)
        func = self.params.func
        out = diffGen.diff(func)
        return(out)


class Bdp(Term):

    def set_base(self, term):
        
        '''Used for fill local data'''

        '''Orders and varList will be set here
        from term's pattern (like {x, 2})
        Return delay data
        '''
        delay_data = self.set_delay(term)
        self.set_var_index(term)

        if delay_data is not None:
            return({'delay_data': delay_data})
        else:
            return(None)

    def set_point(self, point):
        self.params.point = point

    def print_cpp(self):
        return(self.var_point())

    def var_point(self):
        '''
        DESCRIPTION:
        For patterns like
        U(t,{x,0.7})
        U(t,{x,0.7}{y,0.3})
        '''
        
        if self.params.dim == 1:
            try:
                x = self.params.point[0]
            except:
                raise(BaseException('for var point 1d set point = [val]'))
            return(self.var_point_1d(x))
        elif self.params.dim == 2:
            try:
                x, y = self.params.point
            except:
                raise(BaseException('for var point 2d set point '
                                    + '= [val, val]'))
            return(self.var_point_2d(x, y))

    def var_point_1d(self, x):
        '''
        DESCRIPTION:
        For patterns like U(t,{x,0.7})
        '''
        blockNumber = self.params.blockNumber
        varIndex = self.params.unknownVarIndex
        return('source[delay]['+str(x)+'*idxX'+'*'
               + 'Block'+str(blockNumber)+'CELLSIZE+'
               + str(varIndex)+']')
        
    def var_point_2d(self, x, y):
        '''
        DESCRIPTION:
        For U(t,{x,0.7}{y,0.3})
        '''
        blockNumber = self.params.blockNumber
        varIndex = self.params.unknownVarIndex
        return(('source[delay][('+str(x)+'*idxX'
                + '+'
                + str(y)+'*idxY*Block'
                + str(blockNumber)
                + 'StrideY)*'
                + 'Block'+str(blockNumber)+'CELLSIZE+'
                + str(varIndex)+']'))


class Var(Term):

    def set_base(self, term):

        '''Used for fill local data'''

        '''Orders and varList will be set here
        from term's pattern (like {x, 2})
        Return delay data
        '''

        delay_data = self.set_delay(term)
        self.set_var_index(term)

        if delay_data is not None:
            return({'delay_data': delay_data})
        else:
            return(None)

    def print_cpp(self):
        return(self.var_simple())

    def var_simple(self):
        '''
        DESCRIPTION:
        varIndex usage:
        source[][idx+0] - x
        source[][idx+1] - y
        source[][idx+2] - z
        
        '''
        try:
            varIndex = self.params.unknownVarIndex
            return('source['
                   + 'delay'
                   + '][idx + '
                   + str(varIndex)
                   + ']')
        except:
            raise(BaseException('set varIndex first'))

    def var_1d(self):
        # TODO
        blockNumber = self.params.blockNumber
        varIndex = self.params.unknownVarIndex
        return('source[delay][idx'+'+'+'idxX'+'*'
               + 'Block'+str(blockNumber)+'CELLSIZE'
               + '+'+str(varIndex)+']')
        
    def var_2d(self):
        # TODO
        blockNumber = self.params.blockNumber
        varIndex = self.params.unknownVarIndex
        return(('source[delay][(idx'
                + '+'
                + 'idxX'+'*Block'
                + str(blockNumber)
                + 'StrideY)*'
                + 'Block'+str(blockNumber)+'CELLSIZE'
                + '+'+str(varIndex) + ']'))


class FreeVar(Term):

    def set_base(self, term):

        '''Used for fill local data.
        Extract var_name'''

        self.var_name = term.name.lex[0]

    def print_cpp(self):

        '''x->idxX, y->idxY, z->idxZ '''

        return("idx"+self.var_name.upper())


class Coeffs(Term):

    def set_base(self, term):

        '''Used for fill local data'''

        self.set_coeff_index(term)

    def set_coeff_index(self, term):
        coeffs = term.name.lex[0]
        try:
            self.params.coeffsIndex = self.params.map_cti[coeffs]
        except:
            raise(BaseException('set coeffs_indexes first'))

    def set_coeffs_indexes(self, map_cti):
        self.params.map_cti = map_cti

    def print_cpp(self):
        
        coeffsIndex = self.params.coeffsIndex
        return('params['
               + str(coeffsIndex)
               + ']')


class Pow(Term):

    def set_base(self, term):

        '''Used for fill local data'''

        self.set_pow_degree(term)

    def set_pow_degree(self, term):
        # try:
        # if name is a Word
        right = term.name.lex[0]
        # except AttributeError:
        #     # if name is a str
        #     right = term.name

        self.degree = right.split('^')[1]
        
    def print_cpp(self):
        
        degree = str(self.degree)
        left = "pow("
        right = "," + degree + ")"
        return(left, right)


class Func(Term):

    def set_base(self, term):

        '''Used for fill local data'''

        self.func_name = term.name.lex[0]
        
    def print_cpp(self):
        
        left = self.func_name
        right = ")"
        return(left, right)


def delay_postproc(node):

    '''Convert delays for all term's that have it.
    node have or have not global_data['delay_data'] value.
    If have, it will be transformed into cpp corect
    order (for ex: [5.1, 1.5, 2.7]->[3, 1, 2])

    First it collect delays (and remember from whom)
    then convert them,
    finely replace them into it's term.cpp.out string.

    Examples:
    for node:
       term.cpp.global_data['delay_data'] = (1, 'V(t-1.1)', '1.1')
       term.cpp.out = source[delay]
    return:
       term.cpp.out_new = source[coverted delay for 1.1]

    Return:
    (in sent U*U(t-3.1)*V(t-3.3)*U(t-1.3)*V(t-1.1) ...)

    {'converted_delay': 2, 'delay_data': (1, 'U(t-3.1)', '3.1')}
    for U(t-3.1) where:
    converted_delay : source[converted_delay][0]
    delay_data[0] - number of delay's term U(t-3.1)
                    in all delays terms.

    {'converted_delay': 2, 'delay_data': (2, 'V(t-3.3)', '3.3')}
    for V(t-3.3) where:
    converted_delay : source[converted_delay][1]
    delay_data[0] - number of delay's term V(t-3.3)
                    in all delays terms.

    {'converted_delay': 1, 'delay_data': (3, 'U(t-1.3)', '1.3')}
    for U(t-1.3) where:
    converted_delay : source[converted_delay][0]
    delay_data[0] - number of delay's term U(t-1.3)
                    in all delays terms.
    '''
    out = node

    def convert_delays(delays):

        '''Convert float delay to int,
        according it's value.

        For ex:
        [5.1, 1.5, 2.7]->[3, 1, 2]
        '''
        # delays = copy(delays)
        delays.sort()
        sdelays = [delays.index(val)+1 for val in delays]
        logger.debug(sdelays)
        return(zip(delays, sdelays))

    logger.debug("FROM postproc")

    # FOR factorize terms delays for var:
    # res[val] = [(delay_0, term_id_0), ...]
    res = {}
    for term in out:
        '''
        if type(term) == str:
            continue
        '''
        try:
            delay_data = term.cpp.global_data['delay_data']
            term_id, var, delay = delay_data
            # U(t-1.1)->U
            var = var[0]
            if var in res.keys():
                if delay in res[var].keys():
                    res[var][delay].append(term_id)
                else:
                    res[var][delay] = [term_id]
            else:
                res[var] = {delay: [term_id]}
        except KeyError:
            pass
        except AttributeError:
            # if term not have out:
            # (like +):
            continue
    logger.debug("res")
    logger.debug(res)
    # END FOR

    # FOR map float delays to it's source equivalent:
    # map_dsd: var -> delay, sdelay
    map_dsd = lambda var: convert_delays(list(res[var].keys()))

    # map_td: term_id -> source delay
    map_td = dict([(equal_term, sdelay) for var in res.keys()
                   for delay, sdelay in map_dsd(var)
                   for equal_term in res[var][delay]])
    logger.debug("map_td")
    logger.debug(map_td)
    # END FOR

    # FOR find terms for converted delay:
    out_new = []
    for term in out:
        try:
            '''
            if type(term) == str:
                out_new.append(term)
                continue
            '''
            # if delay
            # transform source[delay]->source[1]:
            delay_data = term.cpp.global_data['delay_data']
            term_id, var, delay = delay_data
            sdelay = map_td[term_id]
            term.cpp.out = term.cpp.out.replace('delay', str(sdelay))
            term.cpp.global_data['converted_delay'] = sdelay
            out_new.append(term)
        except KeyError:
            try:
                # if no delay
                # transform source[delay]->source[0]
                term.cpp.out = term.cpp.out.replace('delay', str(0))
                out_new.append(term)
            except:
                pass
        except AttributeError:
            # if term not have out:
            # (like +):
            out_new.append(term)
    # logger.debug([o.out for o in out_new if type(o) != str])
    # return(out)  # out_new

