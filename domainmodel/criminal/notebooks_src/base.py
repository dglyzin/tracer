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


class BaseState(object):
    def __init__(self):
        object.__init__(self)

        # FOR widgets definition:

        #   FOR labels
        self.labels = {}
        lWelcome = widgets.Label(value='welcome')
        self.labels['welcome'] = lWelcome
        
        lWelcome1 = widgets.Label(value='welcome_next')
        self.labels['welcome_next'] = lWelcome1
        
        #   END FOR

        #   FOR buttons
        self.buttons = {}
        
        bNext = widgets.Button(description="next")
        self.buttons['next'] = bNext

        bBack = widgets.Button(description="back")
        self.buttons['back'] = bBack

        bReinit = widgets.Button(description="reinit")
        self.buttons['reinit'] = bReinit

        bShow = widgets.Button(description="show all")
        self.buttons['show'] = bShow
        #   END FOR

        #   FOR text:
        self.texts = {}
        '''
        tModel = widgets.Label(description='welcome',
                              value='test2d_for_intervals_single.json')
        self.texts['model'] = tModel
        '''
        #   END FOR

        #   FOR others:
        self.others = {}
        # END FOR

        #   FOR tabs:
        self.box_layout = widgets.Layout(display='flex',
                                         flex_flow='column',
                                         align_items='stretch',
                                         border='solid',
                                         width='50%')

        mNode = widgets.Box(children=[lWelcome, bNext],
                            layout=self.box_layout)
        mNode1 = widgets.Box(children=[lWelcome1, bBack, bReinit],
                             layout=self.box_layout)

        self.tabs_input = [[mNode], [mNode1]]
        self.tabs_names = [["welcome"], ["welcome_next"]]

        # current tab:
        self.tab_current_idx = 0
        self.tab_current = self.make_tab(self.tabs_input[self.tab_current_idx])
        self.set_tabs_names(self.tab_current,
                            self.tabs_names[self.tab_current_idx])
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
                self.set_tabs_names(tab_new,
                                    self.tabs_names[self.tab_current_idx])

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
                self.set_tabs_names(tab_new,
                                    self.tabs_names[self.tab_current_idx])

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

    def make_action_for_tab(self, tab_name, tab_current=None):
        
        if tab_name[0] == 'welcome':
            clear_output()
            display("welcome action")
            

