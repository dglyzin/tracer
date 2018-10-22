import os
import json
import shutil

from settings.settings_connection import Connection

import logging

# if using from tester.py uncoment that:
# create logger that child of tester loger
# logger = logging.getLogger('tests.tester.gen_1d')

# if using directly uncoment that:

# create logger
log_level = logging.INFO  # logging.DEBUG
logging.basicConfig(level=log_level)
logger = logging.getLogger('settings_main')
logger.setLevel(level=log_level)


settings_folder = 'settings'
conn_folder = os.path.join(settings_folder, 'conn')
device_conf_folder = os.path.join(settings_folder, 'device_conf')
pathes_folder = os.path.join(settings_folder, 'pathes')


class Settings():
    def __init__(self, model, conn_name, device_conf_name,
                 hd_prefix=None):
        if hd_prefix is not None:
            self.hd_prefix = hd_prefix

            global conn_folder
            global device_conf_folder
            global pathes_folder

            conn_folder = os.path.join(hd_prefix, conn_folder)
            device_conf_folder = os.path.join(hd_prefix, device_conf_folder)
            pathes_folder = os.path.join(hd_prefix, pathes_folder)
        else:
            self.hd_prefix = ''

        self.extract_all_settings()

        if conn_name is not None:
            self.make_connection(name=conn_name)

        self.make_all_pathes(model)
        self.set_device_conf(device_conf_name)

    def extract_all_settings(self):
        '''Extract all settings in::

        ``self.conn, self.device_conf, self.pathes``
        
        Each file will be key in according settings::

           ``settings/conn/conn_base.json -> self.conn['conn_base']``'''
            
        def get_data(sfolder, sfile, hd_prefix=None):
            # print(sfile)
            if hd_prefix is None:
                file_name = os.path.join(sfolder, sfile)
            else:
                file_name = os.path.join(hd_prefix, sfolder, sfile)

            with open(file_name) as f:
                data = json.loads(f.read())
            return(data)

        settings = [dict([(sfile.split('.')[0],
                           get_data(sfolder, sfile, self.hd_prefix))
                          for sfile in os.listdir(sfolder)
                          if sfile.split('.')[-1] == 'json'])
                    for sfolder in
                    [conn_folder, device_conf_folder, pathes_folder]]

        self.conn, self.device_conf, self.pathes = settings

    def set_device_conf(self, name="default"):
        self.device_conf_name = name

    def make_connection(self, name="conn_base"):

        '''
        DESCRIPTION:

        Fill connection object.
        
        INPUTS:

        - ``name`` - is name (without extension) of conn in ``settings/conn``::
        Ex: name = conn_base for file ``settings/conn/conn_base.json``'''

        self.connection = Connection()
        self.connection.fromDict(self.conn[name])
        self.connection.get_password()

    def make_all_pathes(self, model, model_path=None, use_workspace=False):

        '''Creating all pathes for problem'''

        if self.hd_prefix is None:
            hd_path = os.getcwd()
        else:
            hd_path = self.hd_prefix
        hd_path = self.fix_tilde_bug(hd_path, 'hd', 'path')

        if model_path is None:
            model_path = model.project_path
        model_path = self.fix_tilde_bug(model_path, 'model', 'path')

        pathes = self.pathes

        # model pathes:
        pathes['model'] = {}
        pathes['model']['path'] = model_path

        # name without extension:
        pathes['model']['name'] = model.project_name
        pathes['model']['json'] = pathes['model']['name'] + '.json'
        pathes['model']['out_folder'] = 'out'

        # hd pathes:
        pathes['hd'] = {}

        # path to hybriddomain:
        pathes['hd']['hd'] = hd_path

        # path to project folder at hd:
        pathes['hd']['project_path'] = (os.path
                                        .join(hd_path, 'problems',
                                              pathes['model']['path']))
        
        pathes['hd']['json'] = (os.path
                                .join(pathes['hd']['project_path'],
                                      pathes['model']['json']))

        pathes['hd']['out_folder'] = (os.path
                                      .join(pathes['hd']['project_path'],
                                            pathes['model']['out_folder']))
        pathes['hd']['cpp'] = (os.path
                               .join(pathes['hd']['out_folder'],
                                     pathes['model']['name'] + '.cpp'))
        pathes['hd']['dom_txt'] = (os.path
                                   .join(pathes['hd']['out_folder'],
                                         pathes['model']['name'] + '_dom.txt'))
        pathes['hd']['dom_bin'] = (os.path
                                   .join(pathes['hd']['out_folder'],
                                         pathes['model']['name'] + '.dom'))
        pathes['hd']['sh'] = os.path.join(pathes['hd']['out_folder'],
                                          pathes['model']['name'] + '.sh')
        pathes['hd']['so'] = os.path.join(pathes['hd']['out_folder'],
                                          'libuserfuncs.so')
        pathes['hd']['userfuncs'] = os.path.join(hd_path, 'gens', 'hs', 'src',
                                                 'userfuncs.h')

        pathes['hd']['plot'] = os.path.join(pathes['hd']['out_folder'],
                                            'params_plot.txt')

        pathes['hd']['device_conf'] = os.path.join(pathes['hd']['hd'],
                                                   'settings', 'device_conf')
        # hs pathes:
        pathes['hd']['pathes'] = os.path.join(pathes['hd']['hd'],
                                              'settings', 'pathes')

        # hs pathes:
        pathes['hs'] = {}

        # projects folder at server:
        
        workspace = pathes['pathes_hs_base']['Workspace']
        workspace = self.fix_tilde_bug(workspace, 'workspace', 'path')
        pathes['pathes_hs_base']['Workspace'] = workspace

        # traceFolder:
        tracerFolder = pathes['pathes_hs_base']['TracerFolder']
        tracerFolder = self.fix_tilde_bug(tracerFolder, 'tracer', 'folder')
        pathes['pathes_hs_base']['TracerFolder'] = tracerFolder

        # path to solver:
        pathes['hs']['solver'] = os.path.join(tracerFolder,
                                              "hybridsolver", "bin", "HS")

        # path to hd at solver:
        pathes['hs']['hd'] = os.path.join(tracerFolder,
                                          "hybriddomain")

        # hs device_conf:
        pathes['hs']['device_conf'] = os.path.join(pathes['hs']['hd'],
                                                   'settings', 'device_conf')
        # hs pathes:
        pathes['hs']['pathes'] = os.path.join(pathes['hs']['hd'],
                                              'settings', 'pathes')

        # path to project folder at server:
        pathes['hs']['project_path'] = os.path.join(workspace,
                                                    pathes['model']['path'])
        # path to json at server:
        pathes['hs']['json'] = os.path.join(pathes['hs']['project_path'],
                                            pathes['model']['json'])

        #  file at server:
        pathes['hs']['out_folder'] = (os.path
                                      .join(pathes['hs']['project_path'],
                                            pathes['model']['out_folder']))

        # cpp file at server:
        pathes['hs']['cpp'] = (os.path
                               .join(pathes['hs']['out_folder'],
                                     pathes['model']['name'] + '.cpp'))

        # dom file at server:
        pathes['hs']['dom_bin'] = (os.path
                                   .join(pathes['hs']['out_folder'],
                                         pathes['model']['name'] + '.dom'))
        # sh file at server:
        pathes['hs']['sh'] = (os.path
                              .join(pathes['hs']['out_folder'],
                                    pathes['model']['name'] + '.sh'))

        pathes['hs']['postproc'] = os.path.join(tracerFolder,
                                                'hybriddomain',
                                                'solvers', 'hs',
                                                'postproc', 'video',
                                                'postprocessor.py')

        pathes['hs']['plot'] = os.path.join(pathes['hs']['out_folder'],
                                            'params_plot.txt')

    def fix_tilde_bug(self, path, where, name):
        
        '''Replace ``~/`` with ``/home/username``
        where ``username`` from self.connection.
        If ``self.connection`` not setup yet, return
        ``path`` (unchanged).'''
        
        try:
            connection = self.connection
        except AttributeError:
            # do not fix if connection not set:
            logger.debug("cannot fix tilde bug:"
                         + " connection (username) not set")
            return(path)

        # fix tilde bug:
        path = path.replace("~", "/home/" + connection.username)
        # logger.info("%s_%s fixed:" % (where, name))
        # logger.info(path)
        return(path)

    def convert_problems(self):

        '''Convert .json from tests/ to problems/ folders'''

        # cur_dir = os.getcwd()

        source_dirs = [d for d in os.listdir('tests')
                       if ('.' not in d) and 'test' in d.lower()]

        print("source_dirs")
        print(source_dirs)

        for d in source_dirs:
            dist_dir = os.path.join('problems', d)
            source_dir = os.path.join('tests', d)

            files = os.listdir(source_dir)

            if not os.path.exists(dist_dir):
                print("making dir: %s" % (dist_dir))
                os.makedirs(dist_dir)

            for f in files:
                f_dist_dir = os.path.join(dist_dir, f.split('.')[0])
                
                if not os.path.exists(f_dist_dir):
                    print("creating: %s" % f_dist_dir)
                    
                    os.makedirs(f_dist_dir)
                
                f_source = os.path.join(source_dir, f)

                print("copy %s" % (f_source))
                print("to %s " % (f_dist_dir))
                shutil.copy2(f_source, f_dist_dir)
