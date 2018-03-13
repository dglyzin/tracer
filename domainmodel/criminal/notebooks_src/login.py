import ipywidgets as widgets
from IPython.display import display, clear_output, HTML
import os
import json
from glob import glob

from domainmodel.criminal.notebooks_src.base import make_event, BaseState 


class LoginForm(object):

    ''' Set up config file for ssh.
    Or use existing in hybriddomain/config.
    Will update solver cell.'''

    def __init__(self, params, solver_cell=6):

        ''' In params login_file will be added to keys for
        connection by update button.

        solver_cell - cell where solver widget used.
        '''

        object.__init__(self)
        
        self.solver_cell = solver_cell
        self.params = params

        # FOR buttons
        self.buttons = {}

        bLogin = widgets.Button(description="login")
        self.buttons['login'] = bLogin
        
        bClear = widgets.Button(description="clear")
        self.buttons['clear'] = bClear

        bUpdate = widgets.Button(description="use selected")
        self.buttons['update'] = bUpdate
        # END FOR

        # FOR login fields:
        self.texts = {}

        tLogin = widgets.Text(description='login', value='login')
        self.texts['login'] = tLogin
        
        tPass = widgets.Text(description='pass', value='pass')
        self.texts['pass'] = tPass
        
        tWorkspace = widgets.Text(description='workspace',
                                  value='/home/user/projects/lab')
        self.texts['workspace'] = tWorkspace
        
        tTracerFolder = widgets.Text(description='tracerFolder',
                                     value='/home/user/projects/lab')
        self.texts['tracerFolder'] = tTracerFolder
        # END FOR

        # FOR config file choice button
        # (from hybriddomain/config folder):
        self.log_files = []
        self.log_files.extend(glob("config/example/*.json"))
        self.log_files.extend(glob("config/*.json"))

        if len(self.log_files) == 0:
            self.log_files = ["none"]
            dlog_val = "none"
        else:
            dlog_val = self.log_files[0]
        
        lChoice = widgets.Label(value=r'обязательно:')
        self.dlogFile = widgets.Dropdown(
            options=self.log_files,
            value=dlog_val,
            description='config file:')
        # END FOR

        # style:
        self.box_layout = widgets.Layout(display='flex',
                                         flex_flow='column',
                                         align_items='stretch',
                                         border='solid',
                                         width='50%')

        # all together:
        mNode = widgets.Box([tLogin, tPass,
                             tWorkspace, tTracerFolder,
                             bLogin, bClear,
                             lChoice,
                             self.dlogFile,
                             bUpdate],
                            layout=self.box_layout)
        self.scene_node = mNode

    def show(self):
        display(self.scene_node)

    def set_callbacks(self):
        @make_event(self, 'update')
        def on_button_bUpdate(event, self):
            '''
            DESCRIPTION:
            Set value from Dropdown and update solver widget cell
            '''

            clear_output()
            
            # self.params is pointer to global params for solver:
            self.params['login_file'] = self.dlogFile.value

            update_solver = '''
            <script>
            //$( document ).ready(function(){
            
            // update solver cell:
            try {
                for (var i = 4; i < 30; i++){
                      var cell = IPython.notebook.get_cell(i);
                      cell.execute();
                   }
            }
            catch(error){
               console.log("too many cells to update ");
            }
            
            //})
            </script>
            '''  # % (self.solver_cell)

            display(HTML(update_solver))
           
            display("file selected:", self.dlogFile.value)
                    
            # jupyter bug:
            clear_output()
            self.show()

        @make_event(self, 'login')
        def on_button_bLogin(event, self):
            '''
            DESCRIPTION:
            Generate json config file and update Dropdown from
            config folder
            (hybriddomain/config/)
            file name will be like:
               hybriddomain/config/_login_name.json
            '''
            clear_output()
            # display("model choice:", self.others['model'].value)
            
            # fill config file:
            config = {
                "Host": "192.168.10.100",  # corp7.uniyar.ac.ru
                "Port": 22,  # 2222
                "Username": self.texts['login'].value,
                "Password": self.texts['pass'].value,
                "Workspace": self.texts['workspace'].value,
                "TracerFolder": self.texts['tracerFolder'].value
            }
            # generate_files(self.params)
            display(config)

            # save to file
            user_name = "_" + self.texts['login'].value
            login_file = 'config/%s.json' % user_name
            with open(login_file, 'w') as f:
                json.dump(config, f)
            display("file saved")

            # update Dropdown
            self.log_files = []
            self.log_files.extend(glob("config/example/*.json"))
            self.log_files.extend(glob("config/*.json"))
            self.dlogFile.options = self.log_files
            self.dlogFile.value = self.log_files[-1]
            display("Dropdown updated")

            # jupyter bug:
            clear_output()
            self.show()

        @make_event(self, 'clear')
        def on_button_bClear(event, self):
            '''
            DESCRIPTION:
            Delete config file
            '''
            clear_output()
            
            user_file = "_" + self.texts['login'].value + '.json'
            os.remove(os.path.join('config', user_file))
            display("file %s removed" % (user_file))

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
