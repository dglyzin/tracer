
import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import os
from glob import glob

from domainmodel.criminal.notebooks_src.base import make_event
from notebook_run import fill_params, generate_files, run_solver
from tests.test_client import run_cmd_interact


class FrontState(object):
    def __init__(self, config_file_name):
        ''' config_file_name - name of file, for ssh. (from LoginForm).
        
        '''
        object.__init__(self)

        try:
            # fill params for given name:
            # self.params = fill_params(json_file_name)
            self.params = {}
            self.params['login_file'] = config_file_name
            self.show_params()
        except:
            display("choice json file")

        # FOR labels
        self.labels = {}

        lNameM = widgets.Label(value=r'choice model from hybriddomain/tests')
        self.labels['model'] = lNameM
        # END FOR

        # FOR text:
        self.texts = {}

        tModel = widgets.Text(description='model',
                              value='test2d_for_intervals_single.json')
        self.texts['model'] = tModel
        # END FOR

        # FOR buttons
        self.buttons = {}

        bModel = widgets.Button(description="choice model json")
        self.buttons['model'] = bModel
        
        bCompile = widgets.Button(description="compile")
        self.buttons['compile'] = bCompile

        bSolve = widgets.Button(description="solve")
        self.buttons['solve'] = bSolve

        bResult = widgets.Button(description="show result")
        self.buttons['result'] = bResult

        bClear = widgets.Button(description="clear")
        self.buttons['clear'] = bClear
        # END FOR

        # FOR login:

        self.texts = {}
        
        # END FOR

        # FOR others:
        self.others = {}
        
        self.tests = []

        self.tests.extend(glob("tests/gpu1block1d/*.json"))
        self.tests.extend(glob("tests/*.json"))
        self.tests.extend(glob("tests/1dTests/*.json"))
        self.tests.extend(glob("tests/2dTests/*.json"))
        self.tests.extend(glob("tests/3dTests/*.json"))

        dModel = widgets.Dropdown(
            options=self.tests,
            value=self.tests[0],
            description='side:')
        self.others['model'] = dModel
        # END FOR

        box_layout = widgets.Layout(display='flex',
                                    flex_flow='column',
                                    align_items='stretch',
                                    border='solid',
                                    width='50%')
        
        # put all together:
        children = [
            lNameM, dModel,
            # bCompile,
            bSolve, bResult,
            bClear]
        mNode = widgets.Box(children=children,
                            layout=box_layout)
        
        self.scene_node = mNode

    def show(self):
        display(self.scene_node)

    def set_callbacks(self):
        
        @make_event(self, 'compile')
        def on_button_bCompile(event, self):
            '''
            DESCRIPTION:
            Compile file (in jupyter server)
            not used.
            '''
            clear_output()
            # display("model choice:", self.others['model'].value)

            generate_files(self.params)
            display("done")

            # jupyter bug:
            clear_output()
            self.show()

        @make_event(self, 'solve')
        def on_button_bSolve(event, self):
            '''
            DESCRIPTION:
            Run python2 remoterun.py config_file_name model_file
            with -w from model file (dnode1)
                 -p exp
            progress use regexp from stdout.
            '''
            clear_output()
            
            # progress:
            progress_obj = Progress(STEPS=100)
            display(progress_obj.progress)

            # run interactive:
            '''
            script_name = 'tests/test_solver.py'
            cmd = ['python3', script_name, '-s', str(10)]
            '''
            script_name = 'remoterun.py'
            cmd = ['python2', script_name,
                   self.params['login_file'],  # 'config/valdecar.json',
                   self.others['model'].value]
            # 'tests/2dTests/test2d_one_block1.json'

            run_cmd_interact(cmd, o=progress_obj,
                             re_pat=r".*Done (?P<proc>\d\d|\d)")

            # run_solver(self.params)
            # display("done")

            # jupyter bug:
            # clear_output()
            self.show()

        @make_event(self, 'result')
        def on_button_bResult(event, self):
            '''
            DESCRIPTION:
            Show result or link to it.
            '''
            clear_output()
            model_name = (self.others['model'].value).split('.')[0]
            video_file = model_name + '-plot0.mp4'
            self.video_file = video_file
            str_video = '''
            <script>
            </script>

            <video controls>
              <source src="%s" type="video/mp4">
              <!--<source src="rabbit320.webm" type="video/webm">-->
            </video>
            <p>If your browser doesn't support HTML5 video.
                 Here is a <a href="%s">link to the video</a>
                 instead.</p>
           
            ''' % (video_file, video_file)
            
            display(HTML(str_video))
            # display(str_video)
            display(video_file)
            
            # jupyter bug:
            self.show()

        @make_event(self, 'clear')
        def on_button_bClear(event, self):
            '''
            DESCRIPTION:
            Remove video (created with solve).
            '''
            clear_output()
            try:
                # solve button was used
                video_file = self.video_file
                os.remove(self.video_file)
            except:
                try:
                    # solve button was not used:
                    model_name = (self.others['model'].value).split('.')[0]
                    video_file = model_name + '-plot0.mp4'
                    os.remove(video_file)
                except:
                    pass
            # jupyter bug:
            clear_output()
            self.show()

    def show_params(self):
        display("tracer_folder")
        display(self.params['tracerFolder'])
        
        display("out_files_names")
        display(self.params['outFileName']+".*")
        
        display("test_file_path")
        display(self.params['fileName'])
        

class Progress():

    ''' Progress for test_client.py
    that used subprocess interactively
    and update progress from stdout.'''

    def __init__(self, STEPS):

        self.step_progress = 0
        self.progress = widgets.IntProgress(
            value=self.step_progress,
            min=0,
            max=STEPS-1,
            step=1,
            description='solving:',
            bar_style='',  # 'success', 'info', 'warning', 'danger' or ''
            orientation='horizontal'
        )

    def succ(self, val):
        self.progress.value = val
            

