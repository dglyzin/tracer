'''
USAGE:
# test from shell:
hybriddomain$: python3 -m domainmodel.criminal.state

# because of ctypes work correctly only from shell
# cannot directly call solver from  interpreter (or notebook)
# and need to call python3 from there.
# for that pickle used in load/save data:

# generate solver data:

    state = st.State
    state.get_model(modelFile)
    state.set_params()
    # state.plot_block()
    state.parse_equations_w()
    state.gen_src_files()
    self.prepare_to_solver()

    state.save_to_file()

# run solver from shell
    state = st.State()
    state.load_from_file()
    state.run_solver_shell()

# result will be in:
    state.load_from_file()
    state.result
'''
import os

from domainmodel.criminal.parser import Parser
from domainmodel.criminal.cppOutsForGenerators import CppOutsForGenerators as CppOutGen
from domainmodel.criminal.params import Params

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pchs

import sys
import pickle
import subprocess

# python 2 or 3
if sys.version_info[0] > 2:
    from domainmodel.model import Model
    import domainmodel.criminal.mini_solver.main as mn
else:
    from ..model import Model
    import mini_solver.main as mn


class State(object):
    '''
    DESCRIPTION:
    Used for prepare data to solver (src files and input arrays)
    And also for compilation and running solvers.
    See main method.
    '''
    def __init__(self, state=None):
        object.__init__(self)

        # cuda
        self.cuda = False

        # path to solver
        curDir = os.getcwd()
        self.path = os.path.join(curDir,
                                 'domainmodel',
                                 'criminal',
                                 'mini_solver')

        self.file_for_solver_args = os.path.join(os.getcwd(),
                                                 'domainmodel',
                                                 'criminal',
                                                 'tmp_state')

        if state is not None:
            self.model = state.model
            self.params = state.params

    def main(self):
        '''
        DESCRIPTION:
        Test.
        '''
        modelFile = "tests/2dTests/test2d_for_intervals_single.json"
        
        self.get_model(modelFile)
        self.set_params()
        # self.plot_block()
        
        self.parse_equations_w()

        self.gen_src_files()
        self.compile_solver()

        self.prepare_to_solver()
        self.run_solver()
        self.plot_results(interact=False)

    def get_model(self, modelFile):
        # FOR get model
        if type(modelFile) == str:
            self.model = get_model_for_tests(modelFile)
        else:
            self.model = modelFile
        # END FOR
    
    def set_params(self):
        # FOR set params
        self.params = Params()

        self.params.set_params_for_definitions(self.model)

        # for funcNamesStack and bounds and ics from params
        self.params.set_params_for_centrals(self.model)

        self.params.set_params_for_bounds_2d(self.model)

        # for namesAndNumbers
        self.params.set_params_for_array()

        self.params.set_params_for_dom_centrals(self.model)
        try:
            self.params.set_params_for_dom_interconnects()
        except:
            pass

        self.params.set_params_for_dom_bounds(self.model)
        # END FOR

        # remove vertex
        names = self.params.namesAndNumbers[0]
        _test = ['Vertex' not in name for name in names]
        self.params.namesAndNumbers[0] = [name for i, name in enumerate(names)
                                          if _test[i]]

    def parse_equations_w(self):

        # FOR parser
        parser = Parser()

        # FOR kernels equations for centrals
        parser.params.diffType = 'pure'
        parser.params.diffMethod = 'common'
        parser.params.parameters = self.model.params
        parser.params.parametersVal = self.model.paramValues[0]

        for eq in self.params.equations:
            print("eq.values")
            print(eq.values)
            parser.params.blockNumber = eq.blockNumber
            if eq.cpp:
                eq.parsedValues = eq.values
            else:
                eq.parsedValues = [parser.parseMathExpression(value)
                                   for value in eq.values]
        # END FOR

        # FOR kernels equations for bound
        for bound in self.params.bounds:
            if bound.btype == 0:
                # Dirichlet
                bound.parsedValues = bound.values
            else:
                # Neuman
                parser.params.diffType = 'pure'
                # TODO for diffMethod
                # in 2d We should use diff instead diff_special
                # or choice between special and common in action_for_termDiff
                # or in derivCodeGenerator.__init__
                parser.params.diffMethod = 'special'
                parser.params.parameters = self.model.params
                print("PARAMETERS")
                print(parser.cppOut.params.parameters)
                parser.params.parametersVal = self.model.paramValues[0]

                parser.params.blockNumber = bound.blockNumber
                parser.params.side = bound.side

                # bound can be U(t-1, {x, 0.3})
                # so dim and shape needed
                # TODO: for dim
                parser.params.dim = '1D'
                cellSize = 1
                parser.params.shape = [cellSize/float(self.model.gridStepX),
                                       cellSize/float(self.model.gridStepY),
                                       cellSize/float(self.model.gridStepZ)]
                bound.parsedValues = []

                # for derivOrder = 1:
                # du/dx = bound.value[i]
                # for derivOrder = 2:
                # left border
                # ddu/ddx = 2*(u_{1}-u_{0}-dy*bound.value[i])/(dx^2)
                # right border
                # ddu/ddx = 2*(u_{n-1}-u_{n}-dy*bound.value[i])/(dx^2)
                for i, eq in enumerate(bound.equation.system):
                    # parse phi
                    value = parser.parseMathExpression(bound.values[i])
                    parser.cppOut.dataTermMathFuncForDiffSpec = value
                    # parse eq(phi)
                    bound.parsedValues.append(parser.parseMathExpression(eq))
        # END FOR

    def gen_src_files(self):
        if self.cuda:
            self.gen_src_files_cuda()
        else:
            self.gen_src_files_cpp()
        
    def gen_src_files_cuda(self):
        cppOut = CppOutGen()
        out_cuda = cppOut.get_out_for_mini_solver_cuda(self.params)
        path = os.path.join(os.getcwd(),
                            'domainmodel',
                            'criminal',
                            'mini_solver',
                            'cuda',
                            'core.cu')
        to_file(out_cuda, path)

    def gen_src_files_cpp(self):

        # FOR src file generation
        cppOut = CppOutGen()

        #    FOR cpp/include/core.h
        out_h = cppOut.get_out_for_mini_solver_cpp_core(self.params)

        path = os.path.join(os.getcwd(),
                            'domainmodel',
                            'criminal',
                            'mini_solver',
                            'cpp',
                            'include',
                            'core.h')
        print(path)
        to_file(out_h, path)
        #    END FOR

        #    FOR cpp/kernels.cpp
        out_cpp = cppOut.get_out_for_mini_solver_cpp_kernels(self.params)

        path = os.path.join(os.getcwd(),
                            'domainmodel',
                            'criminal',
                            'mini_solver',
                            'cpp',
                            'kernels.cpp')
        
        to_file(out_cpp, path)
        #    END FOR
        # END FOR

    def compile_solver(self):
        # FOR compilation
        if self.cuda:
            mn.compile_cuda(self.path, 1)
        else:
            mn.compile_cpp(self.path, 1)
        # END FOR

    def prepare_to_solver(self, ITERATION_COUNT=128):
        # FOR prepare data to solver:
        #    FOR getting input parameters
        self.funcInit = self.params.fill_2d_init_funcs(self.model)

        functionMap = self.params.functionMaps[0]
        self.funcIdxs = self.params.fill_2d_func_idxs(self.model, functionMap)

        funcIdxs_file = os.path.join(os.getcwd(),
                                     'domainmodel',
                                     'criminal',
                                     'mini_solver',
                                     'funcIdxs_file.txt')
        with open(funcIdxs_file, 'w') as f:
            f.write(str(list(self.funcIdxs)))

        self.parameters = self.params.fill_parameters(self.model)

        print("parameters")
        print(self.parameters)

        print("params.functionMaps")
        print(self.params.functionMaps)
        #    END FOR

        mn.Block0CountY, mn.Block0CountX = self.funcInit.shape
        mn.SIZE_OF_RESULT = mn.Block0CountX * mn.Block0CountY

        self.COUNT_OF_DELAYS = 1
        self.ITERATION_COUNT = ITERATION_COUNT

        self.result = np.zeros((mn.Block0CountY, mn.Block0CountX)).astype('double')
        self.result[:] = self.funcInit[:]
        self.result.astype('double')

        self.source = np.zeros((self.COUNT_OF_DELAYS,
                                mn.Block0CountY, mn.Block0CountX)).astype('double')
        self.source[0][:] = self.funcInit[:]
        self.source = self.source.astype('double')

        self.funcIdxs = self.funcIdxs.astype('int32')

        self.parameters = self.parameters.astype('double')

        # interconnect dont used now
        self.ic = np.zeros((1)).astype('double')
        # END FOR
        
        print(self.result)

    def save_to_file(self):
        '''
        DESCRIPTION:
        Save prepared data to file.
        Requires call self.prepare_to_solver first.
        '''
        solver_args = [self.funcIdxs, self.result, self.source,
                       self.parameters, self.ic,
                       self.ITERATION_COUNT, self.path, self.cuda]

        with open(self.file_for_solver_args, 'wb') as f:
            pickle.dump(solver_args, f)

    def load_from_file(self):
        '''
        DESCRIPTION:
        Reverse task of save_to_file.
        '''
        with open(self.file_for_solver_args, 'rb') as f:
            solver_args = pickle.load(f)

        self.funcIdxs = solver_args[0].astype('int32')
        self.result = solver_args[1].astype('double')
        self.source = solver_args[2].astype('double')
        self.parameters = solver_args[3].astype('double')
        self.ic = solver_args[4].astype('double')
        self.ITERATION_COUNT = int(solver_args[5])
        self.path = solver_args[6]
        self.cuda = bool(solver_args[7])

    def run_solver_shell(self, _stderr=None):
        '''
        DESCRIPTION:
        load data or prepare it first:
        self.load_from_file()
        or
        self.prepare_to_solver()
        
        RETURN:
        Result will be in file_for_solver_args:
        self.load_from_file()
        self.result
        
        # plot:
        result = self.result/self.result.max()
        result = 256*result
        plt.imshow(result)
        
        '''
        cmd = ['python3', '-m', 'domainmodel.criminal.state', 'hello']

        # logger.debug("cmd = %s" % str(cmd))
        print(cmd)
        '''
        stdout and stderr PIPE means
        that new child stream will be created
        so standart output will be unused.
        See:
        https://docs.python.org/2.7/library/subprocess.html#frequently-used-arguments
        https://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.communicate
        '''
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()

        if (err is not None and len(err) > 0
            and _stderr is None):
            raise(GccException(err))
        if _stderr is not None:
            print("out")
            print(out)
            print("err")
            print(err)
        # return(out)

    def run_solver(self):
        print("cuda:")
        print(self.cuda)

        # main code
        mn.solver(self.funcIdxs, self.result, self.source,
                  self.parameters, self.ic,
                  self.ITERATION_COUNT, self.path, self.cuda)
    
    def save_result(self):
        with open(self.file_for_result, 'wb') as f:
            pickle.dump(self.result, f)

    '''
    def load_result(self):
        with open(self.file_for_result, 'wb') as f:
            pickle.dump([self.result, self.source], f)
    '''

    def plot_results(self, interact=True):
        _plt = mn.plot(self.result)
        if interact:
            return(_plt)
        else:
            _plt.show()

    def plot_block(self):
        # FOR PLOT:

        # init plot
        fig = plt.figure()
        ax = fig.add_subplot(111)
        scale = 10
        # draw block
        block = self.model.blocks[-1]

        width_x = block.sizeX * scale
        height_y = block.sizeY * scale

        orign_x = 0
        orign_y = -height_y

        r = pchs.Rectangle((orign_x, orign_y), width=width_x, height=height_y,
                           color='red', alpha=0.4)
        ax.add_patch(r)
        color = 0.1

        # FOR draw equation regions
        for eRegion in block.equationRegions:

            width_x = eRegion.xto-eRegion.xfrom
            width_x = width_x * scale

            height_y = eRegion.yto-eRegion.yfrom
            height_y = height_y * scale

            orign_x = eRegion.xfrom
            orign_x = orign_x * scale

            orign_y = -eRegion.yfrom * scale - height_y

            equation_text = 'e %s' % str(eRegion.equationNumber)
            # equation_text = model.equations[eRegion.equationNumber].system

            # add rectangle at scen
            ax.add_patch(
                pchs.Rectangle((orign_x, orign_y),
                               width=width_x, height=height_y,
                               color=[0.1, 0.1, color], alpha=0.4))

            # add equation text
            plt.annotate(equation_text,
                         xy=(orign_x + width_x/2.0,
                             orign_y + height_y/2.0))
            if color < 1:
                color += 0.1
        # END FOR

        # FOR draw sides
        color = 0.0
        side_border = 3.0
        for side in self.params.new_sides:
            # for last block
            if side['blockNumber'] == self.model.blocks.index(block):
                _block = self.model.blocks[side['blockNumber']]
                for interval in side['side_data']:

                    # default text
                    equation_text = str(interval.name)

                    if side['side'] == 0:

                        width_x = side_border

                        height_y = interval[1] - interval[0]
                        height_y = height_y * scale

                        orign_x = -side_border

                        orign_y = -interval[0] * scale - height_y

                    if side['side'] == 1:

                        width_x = side_border
                        height_y = interval[1] - interval[0]
                        height_y = height_y * scale
                        orign_x = _block.sizeX * scale
                        orign_y = -interval[0] * scale - height_y

                    if side['side'] == 2:

                        width_x = interval[1] - interval[0]
                        width_x = width_x * scale
                        height_y = side_border
                        orign_x = interval[0] * scale
                        orign_y = 0

                        equation_text = 'b: %s \n' % str(interval.name['b'])
                        equation_text += 'e: %s' % str(interval.name['e'])

                    if side['side'] == 3:

                        width_x = interval[1] - interval[0]
                        width_x = width_x * scale
                        height_y = side_border
                        orign_x = interval[0] * scale
                        orign_y = -_block.sizeY * scale - side_border

                        equation_text = 'b: %s \n' % str(interval.name['b'])
                        equation_text += 'e: %s' % str(interval.name['e'])

                    if color < 1.0:
                        color += 0.05

                    # add rectangle at scen
                    ax.add_patch(
                        pchs.Rectangle((orign_x, orign_y),
                                       width=width_x, height=height_y,
                                       color=[0.3, 0.3, color], alpha=0.4))
                    # add equation text
                    plt.annotate(equation_text,
                                 xy=(orign_x + width_x/2.0,
                                     orign_y + height_y/2.0))
        # END FOR

        # FOR draw vertex
        vertex_border = 1.0
        for vertex in self.params.bounds_vertex:
            # for last block
            if vertex.blockNumber == self.model.blocks.index(block):
                _block = self.model.blocks[vertex.blockNumber]

                if vertex.sides == [0, 2]:
                    orign_x = -side_border
                    orign_y = side_border
                elif(vertex.sides == [2, 1]):
                    orign_x = _block.sizeX * scale + side_border/2.0
                    orign_y = side_border
                elif(vertex.sides == [1, 3]):
                    orign_x = _block.sizeX * scale + side_border
                    orign_y = -_block.sizeY * scale - 3.7*side_border

                elif(vertex.sides == [3, 0]):
                    orign_x = - side_border
                    orign_y = -_block.sizeY * scale - 3.7*side_border

                equation_text = 'v: %s \n' % str(vertex.sides)
                equation_text += 'b: %s \n' % str(vertex.boundNumber)
                equation_text += 'e: %s' % str(vertex.equationNumber)

                # add equation text
                plt.annotate(equation_text,
                             xy=(orign_x,
                                 orign_y))
        # END FOR

        plt.xlim(-2*side_border, block.sizeX*scale+2*side_border)
        plt.ylim(-block.sizeY*scale-4.5*side_border, 0+side_border)

        plt.annotate('$ \omega= \leq = \{(x,y)|x\leq y\}$',
                     xy=(4, 7))

        path = os.path.join(os.getcwd(), 'tests',
                            'introduction',
                            'src',
                            'from_test_template_bounds_2d.png')
        print("path")
        print(path)
        # plt.savefig(path)
        return(plt)
        # END FOR


def get_model_for_tests(modelFile="tests/2dTests/test2d_for_intervals_single.json"):
    '''
    DESCRIPTION:
    What is model.
    Create model for all tests.
    '''
    model = Model()
    model.loadFromFile(modelFile)
    return(model)


def to_file(out, path):
    
    '''
    path = os.path.join(os.getcwd(),
                        'domainmodel',
                        'criminal',
                        'mini_solver',
                        name)
    '''
    print("path =")
    print(path)
    f = open(path, 'w')
    f.write(out)
    f.close()


class GccException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err


if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) > 1:
        state = State()
        state.load_from_file()
        print(state.source)
        print(state.result)
        print(state.funcIdxs)
        print(state.parameters)
        print(state.ic)
        print(state.ITERATION_COUNT)
        print(state.path)
        state.compile_solver()
        state.run_solver()

        state.save_to_file()
        # state.plot_results()
    else:
        state = State()
        state.cuda = True
        state.main()
        print("result")
        print(state.result)
