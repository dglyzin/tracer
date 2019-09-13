from gens.hs.gen_env.postproc.postproc_main import Postproc

from gens.hs.gen_env.cpp.env.definitions.def_main import Gen as GenDef
from gens.hs.gen_env.cpp.env.initials.initials_main import Gen as GenInit
from gens.hs.gen_env.cpp.env.params.params_main import Gen as GenParams
from gens.hs.gen_env.cpp.env.centrals.cent_main import Gen as GenCent
from gens.hs.gen_env.cpp.env.bounds.bounds_main import GenD1 as GenBoundsD1
from gens.hs.gen_env.cpp.env.bounds.bounds_main import GenD2 as GenBoundsD2

from gens.hs.gen_env.cpp.env.ics.ics_main import GenD1 as GenIcsD1
from gens.hs.gen_env.cpp.env.ics.ics_main import GenD2 as GenIcsD2

from gens.hs.gen_env.cpp.env.array.array_main import Gen as GenArr

from gens.hs.gen_env.fm.centrals.fm_cent import GenFmCent
from gens.hs.gen_env.fm.d1.fm_d1 import GenFmD1
from gens.hs.gen_env.fm.d2.fm_d2 import GenFmD2

# from gens.hs.arrays_filler.filler_main import Filler

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('gen_1d')

# if using directly uncoment that:

# create logger
log_level = logging.DEBUG  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('gen_dim')
logger.setLevel(level=log_level)


class GenBase():
    '''
    Generate cpp file.
    Generate functionMaps dict which is:
    
    :doc:`overview <overview>`

    I. Одномерный случай.

    - Группа 1:

        - Центральная функция уравнения по умолчанию

        - Центральные функции уравнений из регионов уравнений
        пользователя в том порядке, в котором они встречаются
        в регионах уравнений данного блока. Без повторений

        - Функция на границе x=0
        - Функция на границе x=x_max

    Пример словаря::

        { center_default : 0
          center: [  [ 1, xfrom, xto],
                        [ 2, xfrom, xto],
                        [ 1, xfrom, xto],
                        [ 2, xfrom, xto],
                     ]
          side0: 3
          side1: 4}

    II. Двумерный случай:

    - `Группа 1`:

        - Центральная функция уравнения по умолчанию

        - Центральные функции уравнений из регионов уравнений
         пользователя в том порядке, в котором они встречаются
         в регионах уравнений данного блока. Без повторений
        
        - Центральная функция уравнениs from equationRegions
        -Функция на границе x=0 y=0
        -Функция на границе x=x_max y=0
        -Функция на границе x=0 y=y_max
        -Функция на границе x=x_max y=y_max

    - `Группа 2`: Функции на границе y=0 в том порядке,
    в котором они впервые встречаются при увеличении значения x.
    Без повторений

    - `Группа 3`: Функции на границе y=y_max в том порядке,
    в котором они впервые встречаются при увеличении значения x.
    Без повторений

    - `Группа 4`: Функции на границе x=0 в том порядке,
    в котором они впервые встречаются при увеличении значения y.
    Без повторений

    - `Группа 5`: Функции на границе x=x_max в том порядке,
    в котором они впервые встречаются при увеличении значения y.
    Без повторений

    Ex::

        { center_default : 0
          center: [  [ 1, xfrom, xto, yfrom, yto],
                        [ 2, xfrom, xto, yfrom, yto],
                        [ 1, xfrom, xto, yfrom, yto],
                        [ 2, xfrom, xto, yfrom, yto],
                     ],
          v02: 3
          v12: 4
          v03: 5
          v13: 6
          side2: [   [ 7, xfrom, xto, yfrom, yto],
                        [ 8, xfrom, xto, yfrom, yto],
                        [ 9, xfrom, xto, yfrom, yto],
                        [ 9, xfrom, xto, yfrom, yto],
                    ]
          side3:
          side0:
          side1:}

    III. Трехмерный случай

    - `Группа 1`:

        - Центральная функция уравнения по умолчанию
        
        - Центральные функции уравнений из регионов уравнений
         пользователя в том порядке, в котором они встречаются
         в регионах уравнений данного блока (На самом деле
         порядок не так уж и важен, ведь в этом словаре указаны
         диапазоны клеток матрицы для каждой центральной функции).
         Без повторений

        - Функция на границе x=0 y=0 z=0
        - Функция на границе x=x_max y=0 z=0
        - Функция на границе x=0 y=y_max z=0
        - Функция на границе x=x_max y=y_max z=0
        - Функция на границе x=0 y=0 z=z_max
        - Функция на границе x=x_max y=0 z= z_max
        - Функция на границе x=0 y=y_max z= z_max
        - Функция на границе x=x_max y=y_max z= z_max

    - `Группа2`: Функции на ребре x=0 y=0 не важно в каком порядке
    и без повторений.

    - `Группа3`: Функции на ребре x=0 y=y_max не важно в каком порядке
    и без повторений.

    - `Группа4`: Функции на ребре x=x_max y=0 не важно в каком порядке
    и без повторений.

    - `Группа5`: Функции на ребре x=x_max y=y_max не важно в каком порядке
    и без повторений.

    - `Группа6`: Функции на ребре x=0 z=0 не важно в каком порядке
    и без повторений.

    - `Группа7`: Функции на ребре x=0 z=z_max не важно в каком порядке
    и без повторений.

    - `Группа8`: Функции на ребре x=x_max z=0 не важно в каком порядке
    и без повторений.

    - `Группа9`: Функции на ребре x=x_max z=z_max не важно в каком порядке
    и без повторений.

    - `Группа10`: Функции на ребре z=0 y=0 не важно в каком порядке
    и без повторений.

    - `Группа11`: Функции на ребре z=z_max y=0 не важно в каком порядке
    и без повторений.

    - `Группа12`: Функции на ребре z=0 y=y_max не важно в каком порядке
    и без повторений.

    - `Группа13`: Функции на ребре z=z_max y=y_max не важно в каком порядке
    и без повторений.


    - `Группа 14`: Функции на границе y=0 не важно в каком порядке.
    Без повторений

    - `Группа 15`: Функции на границе y=y_max не важно в каком порядке.
    Без повторений

    - `Группа 16`: Функции на границе x=0 не важно в каком порядке.
    Без повторений

    - `Группа 17`: Функции на границе x=x_max не важно в каком порядке.
    Без повторений

    - `Группа 18`: Функции на границе z=0 не важно в каком порядке.
    Без повторений

    - `Группа 19`: Функции на границе z=z_max не важно в каком порядке.
    Без повторений

    Ex::

        { center_default : 0
          center: [  [ 1, xfrom, xto, yfrom, yto, zfrom, zto],
                        [ 2, xfrom, xto, yfrom, yto, zfrom, zto],
                        [ 1, xfrom, xto, yfrom, yto, zfrom, zto],
                        [ 2, xfrom, xto, yfrom, yto, zfrom, zto],
                     ],
          v024: 3
          ...
          edge 02: [
                         [11, xfrom, xto, yfrom, yto, zfrom, zto],
                         [12, xfrom, xto, yfrom, yto, zfrom, zto]
                     ]
          edge03:
        ...
          side4: [
            [18, xfrom, xto, yfrom, yto, zfrom, zto],
                        [19, xfrom, xto, yfrom, yto, zfrom, zto],
                        [19, xfrom, xto, yfrom, yto, zfrom, zto],
                        [20, xfrom, xto, yfrom, yto, zfrom, zto]
                     ]
          ...
        }
    '''
    def __init__(self, net, dim):

        self.net = net

        self.postproc = Postproc(self)

        self.dim = dim
        self.model = net.model
        self.delays = []

    def gen_cpp(self):

        '''
        DESCRIPTION::

        Generate cpp for 1d/2d.

        out will be in::

           ``self.cpp_out``
           ``self.funcNamesStack``
           ``self.namesAndNumbers``
        '''
        model = self.model
 
        out = ""

        # out for definitions
        gen_def = GenDef()
        gen_def.common.set_params_for_definitions(model)

        # out for initials:
        gen_init = GenInit()
        gen_init.cpp.set_params_for_initials(model)

        # out for params:
        gen_params = GenParams()
        gen_params.cpp.set_params_for_parameters(model)

        funcNamesStack = []
        
        # out and funcNames for centrals:
        gen_cent = GenCent()
        gen_cent.common.set_params_for_centrals(model, funcNamesStack)

        # out and funcNames for ics:
        if self.dim == 1:
            gen_ics = GenIcsD1()
        elif self.dim == 2:
            gen_ics = GenIcsD2()
        else:
            raise(BaseException("dim %s not supported yet" % self.dim))

        gen_ics.common.set_params_for_interconnects(model, funcNamesStack)

        # out and funcNames for bounds:
        if self.dim == 1:
            gen_bounds = GenBoundsD1()
        elif self.dim == 2:
            gen_bounds = GenBoundsD2()
        else:
            raise(BaseException("dim %s not support yet" % self.dim))

        gen_bounds.common.set_params_for_bounds(model, funcNamesStack,
                                                ics=gen_ics.params.ics)
        
        ### FOR remove duplicates:
        tmp = []
        for funcName in funcNamesStack:
            if funcName not in tmp:
                tmp.append(funcName)
        funcNamesStack = tmp

        # this solution:
        # funcNamesStack = list(set(funcNamesStack))
        # is depricated because set change order
        # each time.
        ### END FOR

        # out and namesAndNumbers:
        gen_arr = GenArr()
        gen_arr.common.set_params_for_array(funcNamesStack)
        namesAndNumbers = gen_arr.params.namesAndNumbers

        '''
        for vertex in gen_bounds.params.bounds_vertex:
            print("vertex.parsedValues:")
            print(vertex.parsedValues)
        '''

        # FOR postproc:
        ### FOR delays:
        # use gen_bounds.params.bounds in order to replace
        # delays in both bounds_edges and bounds_vertex:
        delays = self.postproc.postporc_delays([gen_cent.params,
                                                gen_bounds.params.bounds,
                                                gen_ics.params.ics])
        '''
        for vertex in gen_bounds.params.bounds_vertex:
            print("vertex.parsedValues:")
            print(vertex.parsedValues)
        '''
        logger.info("delays:")
        logger.info(delays)
        sizes_delays = dict([(len(delays[var]), delays[var])
                             for var in delays])
        try:
            max_delays_seq = sizes_delays[max(sizes_delays)]
            self.delays = max_delays_seq
            logger.info("max_delays_seq:")
            logger.info(max_delays_seq)
        except ValueError:
            self.delays = []
        ### END FOR
        
        ### FOR Dirichlet:
        # only after for delays (because postporc_delays rewrite output)
        self.postproc.postproc_dirichlet([gen_bounds.params.bounds])
        ### END FOR
        # END FOR
        out += gen_def.cpp_render.get_out_for_definitions()
        out += gen_init.cpp_render.get_out_for_initials()
        out += gen_params.cpp_render.get_out_for_parameters()
        out += gen_cent.cpp_render.get_out_for_centrals()
        out += gen_bounds.cpp_render.get_out_for_bounds()
        if self.dim == 2:
            # print("parsedValues:")
            # print(gen_bounds.params.bounds_vertex[0].parsedValues)
            out += gen_bounds.cpp_render.get_out_for_bounds(vertex=True)
        
        out += gen_ics.cpp_render.get_out_for_interconnects()
        out += gen_arr.cpp_render.get_out_for_array()

        self.cpp_out = out
        self.funcNamesStack = funcNamesStack
        self.namesAndNumbers = namesAndNumbers

    def gen_dom(self):
        '''
        DESCRIPTION::

        Generate funcs indexes and regions
        for 1d/2d env.

        out will be in:

           ``self.functionMaps``
        '''
        model = self.model

        gen_cent = GenCent()

        if self.dim == 1:
            gen_bounds = GenBoundsD1()
            gen_ics = GenIcsD1()
            
        elif self.dim == 2:
            gen_bounds = GenBoundsD2()
            gen_ics = GenIcsD2()
        else:
            raise(BaseException("dim %s not support yet" % self.dim))

        gen_array = GenArr()

        # FOR funcNameStack
        funcNamesStack = []

        gen_cent.common.set_params_for_centrals(model, funcNamesStack)
        logger.debug("funcNamesStack after cent:")
        logger.debug(funcNamesStack)

        gen_ics.common.set_params_for_interconnects(model, funcNamesStack)
        logger.debug("funcNamesStack after ics:")
        logger.debug(funcNamesStack)

        (gen_bounds.common
         .set_params_for_bounds(model,
                                funcNamesStack, ics=gen_ics.params.ics))
        logger.debug("funcNamesStack after bounds:")
        logger.debug(funcNamesStack)

        ### FOR remove duplicates:
        tmp = []
        for funcName in funcNamesStack:
            if funcName not in tmp:
                tmp.append(funcName)
        funcNamesStack = tmp

        # this solution:
        # funcNamesStack = list(set(funcNamesStack))
        # is depricated because set change order
        # each time.
        ### END FOR
        logger.debug("funcNamesStack after set:")
        logger.debug(funcNamesStack)

        # for namesAndNumbers:
        gen_array.common.set_params_for_array(funcNamesStack)
        namesAndNumbers = gen_array.params.namesAndNumbers
        logger.debug("namesAndNumbers after array:")
        logger.debug(namesAndNumbers)

        # FOR functionMaps:
        functionMaps = {}
        fm_gen_cent = GenFmCent()
        params_eregions = gen_cent.params
        (fm_gen_cent
         .set_params_for_dom_centrals(params_eregions, model,
                                      namesAndNumbers, functionMaps))
        if self.dim == 1:
            fm_gen = GenFmD1()
            
            params_vertexs = (gen_bounds.params.bounds.nodes
                              + gen_ics.params.ics)
            '''
            # this also work:
            params_vertexs = [block.vertexs[v_num].fm
                              for block in model.blocks
                              for v_num in block.vertexs]
            '''
            fm_gen.gen_fm_for_vertexs(params_vertexs,
                                      functionMaps, namesAndNumbers)
            # functionMaps.extend(gen_bounds.params.functionMaps)

        elif self.dim == 2:

            fm_gen = GenFmD2()
            
            # for vertexs:
            params_vertexs = gen_bounds.params.bounds_vertex
            fm_gen.gen_fm_for_vertexs(params_vertexs,
                                      functionMaps, namesAndNumbers)
            
            # for edges:
            params_intervals = [interval for block in model.blocks
                                for side_num in block.sides
                                for interval in block.sides[side_num].intervals
                                if 'fm' in interval.name.keys()]
            fm_gen.gen_fm_for_edges(params_intervals, model,
                                    functionMaps, namesAndNumbers)
        # END FOR
        
        self.funcNamesStack = funcNamesStack
        self.namesAndNumbers = namesAndNumbers
        self.functionMaps = functionMaps

    '''
    def gen_arrays(self):

        self.gen_dom()
        self.filler = Filler(self.model, self.functionMaps, self.delays)
        self.filler.fill_arrays()
    '''
        

class GenD1(GenBase):
    def __init__(self, net):
        GenBase.__init__(self, net, 1)


class GenD2(GenBase):
    def __init__(self, net):
        GenBase.__init__(self, net, 2)
