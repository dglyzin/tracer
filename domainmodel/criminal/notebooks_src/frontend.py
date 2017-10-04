import functools
import ipywidgets as widgets
from IPython.display import display, clear_output
import os
import numpy as np
from pandas import DataFrame
from copy import deepcopy as copy
import matplotlib.pyplot as plt


# send data (fState) to callback(event, fState)
# and wrap it as callback(event)
# and make it as callback for fState.buttons[button_name]
def make_event(fState, button_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(event):
            func(event, fState)
        # make callback for button
        fState.buttons[button_name].on_click(wrapper)
        return(wrapper)
    return(decorator)


class FrontState(object):
    def __init__(self, state):
        object.__init__(self)

        self.state = state

        # FOR widgets definition:

        #   FOR labels
        self.labels = {}

        lNameM = widgets.Label(value=r'choice model from tests/2dTests')
        self.labels['model'] = lNameM

        lNameE = widgets.Label(value='adding equation regions')
        self.labels['equations'] = lNameE

        lNameB = widgets.Label(value='adding bound regions')
        self.labels['bounds'] = lNameB

        lNameI = widgets.Label(value='block image')
        self.labels['image'] = lNameI

        lNameC = widgets.Label(value='compile src out')
        self.labels['compile'] = lNameC

        lNameS = widgets.Label(value='solver params')
        self.labels['solver'] = lNameS

        lNameR = widgets.Label(value='result')
        self.labels['result'] = lNameR
        #   END FOR

        #   FOR buttons
        self.buttons = {}
        
        bNext = widgets.Button(description="next")
        self.buttons['next'] = bNext

        bBack = widgets.Button(description="back")
        self.buttons['back'] = bBack

        bReinit = widgets.Button(description="reinit")
        self.buttons['reinit'] = bReinit

        bAdd = widgets.Button(description="add")
        self.buttons['add'] = bAdd

        bShow = widgets.Button(description="show all")
        self.buttons['show'] = bShow

        bModel = widgets.Button(description="set model")
        self.buttons['model'] = bModel
        #   END FOR

        #   FOR text:
        self.texts = {}
        tModel = widgets.Text(description='model',
                              value='test2d_for_intervals_single.json')
        self.texts['model'] = tModel

        tFrom = widgets.Text(description='from', value='0')
        self.texts['from'] = tFrom

        tTo = widgets.Text(description='to', value='size')
        self.texts['to'] = tTo

        tXfrom = widgets.Text(description='xFrom', value='0')
        self.texts['x from'] = tXfrom

        tXto = widgets.Text(description='xTo', value='sizeX')
        self.texts['x to'] = tXto

        tYfrom = widgets.Text(description='yFrom', value='0')
        self.texts['y from'] = tYfrom

        tYto = widgets.Text(description='yTo', value='sizeY')
        self.texts['y to'] = tYto

        tFuncWDV = r"U' = D[U,{x, 2}]"
        tFuncEW = widgets.Text(description=r"eq:", value=tFuncWDV)
        self.texts['func equations wolfram'] = tFuncEW

        tFuncCDV = 'reuslt[idx + 0] = source[idx]+DT*DXM2*(source[idx+1]-2*source[idx]+source[idx-1])'
        tFuncEC = widgets.Text(description=r"eq: ", value=tFuncCDV)
        self.texts['func equations c++'] = tFuncEC

        tFuncBDV = r"300.0"
        tFuncBW = widgets.Text(description=r"val:", value=tFuncBDV)
        self.texts['func bounds wolfram'] = tFuncBW

        tSolverC = widgets.Text(description=r"ITERATION\nCOUNT: ", value="128")
        self.texts['solver count of iteration'] = tSolverC

        tSolverS = widgets.Text(description=r"ITERATION\nSTEP: ", value="32")
        self.texts['interactive plot step'] = tSolverS
        #   END FOR

        #   FOR others:
        self.others = {}

        dSide = widgets.Dropdown(
            options={'x=0': 0, 'x=xmax': 1, 'y=0': 2, 'y=ymax': 3},
            value=0,
            description='side:')
        self.others['side'] = dSide

        rBtype = widgets.RadioButtons(
            options=['Neumann', 'Dirichlet'],
            value='Dirichlet',
            description='Bound type:',
            disabled=False)
        self.others['btype'] = rBtype

        cCuda = widgets.Checkbox(
            value=False,
            description='cuda',
            disabled=False)
        self.others['cuda'] = cCuda

        # rInter = widgets.interactive(f, x=0)

        #   END FOR

        #   FOR child, nodes, accordions and tabs:
        
        wChildrenE = [lNameE, tXfrom, tXto, tYfrom, tYto, tFuncEW,
                      bAdd, bShow, bBack, bNext]
        cChildrenE = [lNameE, tXfrom, tXto, tYfrom, tYto, tFuncEC,
                      bAdd, bShow, bBack, bNext]

        wChildrenB = [lNameB,
                      dSide, rBtype,
                      tFrom, tTo, tFuncBW,
                      bAdd, bShow,
                      bBack, bNext]

        mNode = widgets.Box(children=[lNameM, tModel, bModel, bNext])

        eNode1 = widgets.Box(children=wChildrenE)
        eNode2 = widgets.Box(children=cChildrenE)

        bNode1 = widgets.Box(children=wChildrenB)

        iNode = widgets.Box(children=[lNameI, bBack, bNext])
        cNode = widgets.Box(children=[lNameC, bBack, bNext])
        sNode = widgets.Box(children=[lNameS, tSolverC, tSolverS,
                                      cCuda,
                                      bBack, bNext])

        
        # for interact usage later
        self.rChildren = [lNameR, bReinit,]
        rNode = widgets.Box(children=self.rChildren)

        self.accordions = {}

        wAccordion = widgets.Accordion(children=[eNode1, bNode1])
        wAccordion.set_title(0, 'equations regions')
        wAccordion.set_title(1, 'bounds regions')
        self.accordions['wolfram'] = wAccordion

        cAccordion = widgets.Accordion(children=[eNode2])
        cAccordion.set_title(0, 'equation regions')
        self.accordions['c++'] = cAccordion

        self.tabs_input = [[mNode], [wAccordion, cAccordion], [iNode],
                           [sNode], [rNode]]
        self.tabs_names = [["set model"], ['wolfram', 'c++'], ['block image'],
                           ['solver params'], ['results']]

        # current tab:
        self.tab_current_idx = 0
        self.tab_current = self.make_tab(self.tabs_input[self.tab_current_idx])
        self.set_tabs_names(self.tab_current, self.tabs_names[self.tab_current_idx])
        #   END FOR
        # END FOR

    def show(self):
        display(self.tab_current)

    def make_tab(self, children):
        return(widgets.Tab(children=children))

    def set_tabs_names(self, tab, names):
        for i, name in enumerate(names):
            tab.set_title(i, name)

    def set_callbacks(self):
        '''
        PATTERNS:
        @make_event(self)
        def on_button(event, self):
            pass
        # self.callbacks['bNext'] = on_button
        self.buttons['bNext'].on_click(on_button)
        '''

        @make_event(self, 'next')
        def on_button_bNext(event, self):
            '''
            DESCRIPTION:
            Go to next tab in self.tabs_input list.
            '''
            clear_output()
            display("next clicked")
            display(self.tab_current_idx)
            if (self.tab_current_idx + 1 < len(self.tabs_input)):

                # main button task
                self.make_action_for_tab(self.tabs_names[self.tab_current_idx],
                                         self.tab_current)
                # close previus tab:
                self.tab_current.close()

                # change index and create new tab:
                self.tab_current_idx += 1
                tab_new = self.make_tab(self.tabs_input[self.tab_current_idx])
                self.set_tabs_names(tab_new, self.tabs_names[self.tab_current_idx])

                # save new tab as current:
                self.tab_current = tab_new

                display(tab_new)
            else:
                display("last tab")
            display(self.tab_current_idx)

            # tabs.open()
            #display(Math("interp\ f(x)="+lg.latex(l.iF)))

        @make_event(self, 'back')
        def on_button_bBack(event, self):
            '''
            DESCRIPTION:
            Go back itro self.tabs_input sequence.
            '''
            clear_output()
            # f=strFunct.value
            display("back clicked")
            display(self.tab_current_idx)
            if (self.tab_current_idx > 0):

                # close previus tab:
                self.tab_current.close()

                # change index and create new tab:
                self.tab_current_idx -= 1
                tab_new = self.make_tab(self.tabs_input[self.tab_current_idx])
                self.set_tabs_names(tab_new, self.tabs_names[self.tab_current_idx])

                # save new tab as current:
                self.tab_current = tab_new

                # show it
                display(tab_new)
            else:
                display("first tab")
            display(self.tab_current_idx)

        @make_event(self, 'reinit')
        def on_button_bReinit(event, self):
            clear_output()

            # main button task
            self.make_action_for_tab(self.tabs_names[self.tab_current_idx],
                                     self.tab_current)

            # close previus tab:
            self.tab_current.close()

            # change index and create new tab:
            self.tab_current_idx = 0
            tab_new = self.make_tab(self.tabs_input[self.tab_current_idx])
            self.set_tabs_names(tab_new, self.tabs_names[self.tab_current_idx])

            # save new tab as current:
            self.tab_current = tab_new
            display(self.tab_current)

        @make_event(self, 'add')
        def on_button_bAdd(event, self):
            clear_output()

            display(self.accordions['wolfram'].selected_index)
            display(self.accordions['c++'].selected_index)
            
            if((self.accordions['wolfram'].selected_index == 0
                and self.tab_current.selected_index == 0)
               or (self.accordions['c++'].selected_index == 0
                   and self.tab_current.selected_index == 1)):
                self.add_region(_type='equation')
                eRegionLast = self.state.model.blocks[0].equationRegions[-1]
                self.show_region(eRegionLast, _type='equation')
            elif((self.accordions['wolfram'].selected_index == 1
                  and self.tab_current.selected_index == 0)):
                self.add_region(_type='bound')
                bRegionLast = self.state.model.blocks[0].boundRegions[-1]
                self.show_region(bRegionLast, _type='bound')
                
            # display(Math("interp\ f(x)="+lg.latex(l.iF)))

        @make_event(self, 'show')
        def on_button_bShow(event, self):
            clear_output()
            
            display(self.accordions['wolfram'].selected_index)
            display(self.accordions['c++'].selected_index)
            
            if((self.accordions['wolfram'].selected_index == 0
                and self.tab_current.selected_index == 0)
               or (self.accordions['c++'].selected_index == 0
                   and self.tab_current.selected_index == 1)):
                display("equations")
                eRegions = self.state.model.blocks[0].equationRegions
                for eRegion in eRegions:
                    self.show_region(eRegion, _type='equation')
            elif(self.accordions['wolfram'].selected_index == 1
                 and self.tab_current.selected_index == 0):
                display("bounds")
                bRegions = self.state.model.blocks[0].boundRegions
                for bRegion in bRegions:
                    self.show_region(bRegion, _type='bound')

        @make_event(self, 'model')
        def on_button_bModel(event, self):
            clear_output()
            mName = self.texts['model'].value
            path = os.path.join("tests", "2dTests", mName)
            display(path)
            self.state.get_model(path)

    def make_action_for_tab(self, tab_name, tab_current=None):
        if tab_name[0] == 'model':
            clear_output()
            display("model action")
            mName = self.texts['model'].value
            path = os.path.join("tests", "2dTests", mName)
            display(path)
            self.state.get_model(path)

        elif tab_name[0] == 'wolfram':
            '''
            set_params
            plot_block
            parse_equations_w
            '''
            clear_output()
            self.state.set_params()

            # if all Ok:
            clear_output()

            self.state.plot_block()

            # if wolfram then parse
            if tab_current.selected_index == 0:
                self.state.parse_equations_w()
            else:
                try:
                    self.state.parse_equations_w()
                except:
                    display("equation in model use c++ also")
                # use c++ kernels
                pass

            # if all Ok:
            clear_output()

            display(tab_current.selected_index)
            display("set params action")

        elif tab_name[0] == 'block image':

            clear_output()
            display("show block action")

        elif tab_name[0] == 'solver params':
            clear_output()

            self.state.cuda = bool(self.others['cuda'].value)

            # FOR generate src:
            self.state.gen_src_files()

            # if all Ok:
            clear_output()
            
            self.state.compile_solver()
            # END FOR

            # FOR run solver:
            ITERATION_COUNT = int(self.texts['solver count of iteration'].value)
            self.state.prepare_to_solver(ITERATION_COUNT)

            # if all Ok:
            clear_output()

            ITERATION_STEP = int(self.texts['interactive plot step'].value)
            
            STEPS = int(ITERATION_COUNT/ITERATION_STEP)
            self.state.results = []

            step_progress = 0
            progress = widgets.IntProgress(
                value=step_progress,
                min=0,
                max=STEPS-1,
                step=1,
                description='solving:',
                bar_style='',  # 'success', 'info', 'warning', 'danger' or ''
                orientation='horizontal'
            )
            display(progress)
            for i in range(STEPS):
                clear_output()
                self.state.save_to_file()
                self.state.run_solver_shell()
                self.state.load_from_file()
                self.state.results.append(copy(self.state.result))
                
                # show progress
                step_progress += 1
                progress.value = step_progress
                display("%s " % str(i/float(STEPS-1)*100))
            progress.close()
            # END FOR

            # FOR plot result:

            # if all Ok:
            clear_output()

            # self.state.load_from_file()
            self.state.plot_results()
            
            # normalize:
            for result in self.state.results:
                result = result/result.max()
                result = 256*result

            #   FOR interact widget
            dSteps = STEPS-1

            rSlider = widgets.IntSlider(min=0, max=dSteps,
                                        step=1, value=dSteps)

            def plot_results(step=dSteps):
                plt.imshow(self.state.results[step])
            w = widgets.interactive(plot_results, step=rSlider)

            # add old
            children = self.rChildren[:]

            # add new (can put rSlider as well)
            children.append(w)

            new_node = widgets.Box(children=children)

            # replace result tag inputs
            self.tabs_input[self.tabs_names.index(['results'])] = [new_node]
            #   END FOR
            # END FOR

            display("prepare solver action")
        elif tab_name[0] == 'solve':
            display("solve action")
        elif tab_name[0] == 'results':
            
            # reinit result
            display("print result action")

    def show_region(self, oRegion, _type='equation'):
        
        indexes = ['x', 'y']
        columns = ['from', 'to']

        region = np.zeros((2, 2))

        region[0, 0] = oRegion.xfrom
        region[0, 1] = oRegion.xto
        region[1, 0] = oRegion.yfrom
        region[1, 1] = oRegion.yto
        if _type == 'equation':
            oSystem = self.state.model.equations[oRegion.equationNumber].system
        else:
            bound = self.state.model.bounds[oRegion.boundNumber]
            oSystem = bound.values
            display("side: %d, btype: %d" % (oRegion.side, bound.btype))
            
        display(oSystem)
        display(DataFrame(region, index=indexes, columns=columns))

    def add_region(self, _type='equation'):

        if _type == 'equation':
            oRegions = self.state.model.blocks[0].equationRegions
        else:
            oRegions = self.state.model.blocks[0].boundRegions

        oRegion = copy(oRegions[0])

        if _type == 'equation':
            oRegion.xfrom = float(self.texts['x from'].value)
            oRegion.xto = float(self.texts['x to'].value)
            oRegion.yfrom = float(self.texts['y from'].value)
            oRegion.yto = float(self.texts['y to'].value)
        else:
            oRegion.xfrom = float(self.texts['from'].value)
            oRegion.xto = float(self.texts['to'].value)
            oRegion.yfrom = float(self.texts['from'].value)
            oRegion.yto = float(self.texts['to'].value)

        if _type == 'equation':
            equations = self.state.model.equations
            equation = copy(equations[0])
            if self.tab_current.selected_index == 0:
                equation.system = [self.texts['func equations wolfram'].value]
            elif self.tab_current.selected_index == 1:
                equation.system = [self.texts['func equations c++'].value]
                equation.cpp = True
            equations.append(equation)
            oRegion.equationNumber = len(equations) - 1
        else:
            bounds = self.state.model.bounds
            bound = copy(bounds[0])
            btype_name = self.others['btype'].value
            bound.btype = 0 if btype_name == 'Dirichlet' else 1
            bound.values = [self.texts['func bounds wolfram'].value]
            bounds.append(bound)
            oRegion.boundNumber = len(bounds) - 1
            oRegion.side = int(self.others['side'].value)

        oRegions.append(oRegion)
