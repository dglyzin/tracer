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


class Settings():
    def __init__(self, model, conn_name, device_conf_name, paths_name,
                 hd_prefix=None, pf_prefix=None,
                 workspace=None, username=None):
        '''
        Client side uses ``hd/problems`` and ``hd/settings`` folders
        for storing generated files and settings accordingly.
        Server side uses ``workspace/problems`` and ``workspace/settings``
        instead.

        Inputs:

        - ``conn_name`` -- if ``None``, connection settings will not be
        used.

        - ``hd_prefix`` -- if not ``None`` will be used for access to
        hd.

        - ``workspace`` -- if not ``None`` will be used for all files
        generators and conf_files. Folders "settings" and "problems"
        must exist with all needed inside. Only for solver side.

        - ``username`` -- if ``conn_name`` is ``None`` or there is
        no settings for connection then this name will be used for
        fix tilde bug.
        '''
        if username is not None:
            self.username = username
        else:
            self.username = None

        self.use_pf_prefix = False
        self.use_hd_prefix = False
        self.use_workspace = False
        settings_prefix = ""
        self.hd_prefix = ""
        self.pf_prefix = ""
        self.workspace = None
        self.use_workspace = False

        if workspace is not None:
            workspace = self.fix_tilde_bug(workspace, 'workspace', 'path')
            self.workspace = workspace
            settings_prefix = workspace
            self.use_workspace = True
        else:
            if hd_prefix is not None:
                self.hd_prefix = hd_prefix
                self.use_hd_prefix = True
                settings_prefix = hd_prefix
            else:
                if pf_prefix is not None:
                    if "~" in pf_prefix:
                        raise(BaseException("tilde must not been in pf_prefix"))
                    self.pf_prefix = pf_prefix
                    settings_prefix = pf_prefix
                    self.use_pf_prefix = True
        self.settings_folder = os.path.join(settings_prefix,
                                            settings_folder)

        self.set_path_name(paths_name)
        self.set_device_conf_name(device_conf_name)
        self.set_conn_name(conn_name)

        if self.use_pf_prefix:
            self.extract_all_settings_from_files(self.settings_folder,
                                                 conn_name,
                                                 device_conf_name,
                                                 paths_name)
        else:
            self.get_confs(self.settings_folder)
            self.extract_all_settings()

        # choice current settings files:
        if conn_name is not None:
            self.make_connection(name=conn_name)
        self.set_path(paths_name)
        self.set_device_conf(device_conf_name)

        self.make_all_paths(model)

    def get_confs(self, settings_folder):

        conns_folder = os.path.join(settings_folder, 'conn')
        devices_conf_folder = os.path.join(settings_folder, 'device_conf')
        paths_folder = os.path.join(settings_folder, 'paths')
        self.folders = {"conn": conns_folder,
                        "device_conf": devices_conf_folder,
                        "paths": paths_folder}

    def extract_all_settings_from_files(self, settings_folder,
                                        conn_name,
                                        device_conf_name,
                                        paths_name):
        def get_data(sfolder, sfile):
            # print(sfile)
            file_name = os.path.join(sfolder, sfile)
            with open(file_name) as f:
                data = json.loads(f.read())
            return(data)

        self.device_confs = {}
        self.device_confs[device_conf_name] = get_data(settings_folder,
                                                       device_conf_name + ".json")
        self.paths_confs = {}
        self.paths_confs[paths_name] = get_data(settings_folder,
                                                paths_name + ".json")
        if "Password" in self.paths_confs[paths_name]:
            # remove password to prevend it copying to server:
            self.paths_confs[paths_name].pop("Password")
        self.conns = {}
        self.conns[conn_name] = get_data(settings_folder, conn_name + ".json")

    def extract_all_settings(self):
        '''Extract all settings in::

        ``self.conn, self.device_conf, self.pathes``
        
        Each file will be key in according settings::

           ``settings/conn/conn_base.json -> self.conn['conn_base']``'''
            
        def get_data(sfolder, sfile):
            # print(sfile)
            file_name = os.path.join(sfolder, sfile)
            with open(file_name) as f:
                data = json.loads(f.read())
            return(data)

        # print(self.folders)
        settings = dict([(settings_name,
                          (dict([(sfile.split('.')[0],
                                  get_data(self.folders[settings_name], sfile))
                                 for sfile in os.listdir(self.folders[settings_name])
                                 if sfile.split('.')[-1] == 'json'])
                           if os.path.exists(self.folders[settings_name])
                           else {}))
                         for settings_name in self.folders])
        self.settings = settings
        # print(self.settings)
        self.device_confs = self.settings["device_conf"]
        self.paths_confs = self.settings["paths"]
        self.conns = settings["conn"]

    def set_path_name(self, name):
        if name is None:
            name = "paths_hs_base"
        self.paths_name = name
        
    def set_path(self, name):
        self.paths = self.paths_confs[name]
        
    def set_device_conf_name(self, name="default"):
        self.device_conf_name = name
        logger.info("device_conf_name")
        logger.info(self.device_conf_name)
        
    def set_device_conf(self, name="default"):
        self.device_conf = self.device_confs[name]

    def set_conn_name(self, name):
        self.conn_name = name

    def make_connection(self, name="conn_base"):

        '''
        DESCRIPTION:

        Fill connection object.
        
        INPUTS:

        - ``name`` - is name (without extension) of conn in ``settings/conn``::
        Ex: name = conn_base for file ``settings/conn/conn_base.json``'''
        
        if self.conns == {}:
            raise(BaseException("connection folder not exist"))
        else:
            self.conn = self.conns[name]

        self.connection = Connection()
        self.connection.fromDict(self.conn)
        self.connection.get_password()

    def make_all_paths(self, model, model_path=None):

        '''Creating all pathes for problem'''

        paths = self.paths

        # projects folder at server:
        if self.workspace is None:
            workspace = paths['Workspace']
        else:
            workspace = self.workspace
        workspace = self.fix_tilde_bug(workspace, 'workspace', 'path')
    
        if self.use_pf_prefix:
            hd_path = self.pf_prefix
        else:
            if self.use_hd_prefix:
                hd_path = self.hd_prefix
            else:
                hd_path = os.getcwd()
        hd_path = self.fix_tilde_bug(hd_path, 'hd', 'path')

        if self.use_workspace:
            hd_project_prefix = workspace
        else:
            hd_project_prefix = hd_path

        if model_path is None:
            model_path = model.project_path
        model_path = self.fix_tilde_bug(model_path, 'model', 'path')

        # model pathes:
        paths['model'] = {}
        paths['model']['path'] = model_path

        # name without extension:
        paths['model']['name'] = model.project_name
        paths['model']['json'] = paths['model']['name'] + '.json'
        paths['model']['out_folder'] = 'out'

        # hd paths:
        paths['hd'] = {}

        # path to hybriddomain:
        paths['hd']['hd'] = hd_path

        # path to project folder at hd:
        paths['hd']['project_path'] = (os.path
                                       .join(hd_project_prefix, 'problems',
                                             paths['model']['path']))
        
        paths['hd']['json'] = (os.path
                               .join(paths['hd']['project_path'],
                                     paths['model']['json']))

        paths['hd']['out_folder'] = (os.path
                                     .join(paths['hd']['project_path'],
                                           paths['model']['out_folder']))
        paths['hd']['cpp'] = (os.path
                              .join(paths['hd']['out_folder'],
                                    paths['model']['name'] + '.cpp'))
        paths['hd']['dom_txt'] = (os.path
                                  .join(paths['hd']['out_folder'],
                                        paths['model']['name'] + '_dom.txt'))
        paths['hd']['dom_bin'] = (os.path
                                  .join(paths['hd']['out_folder'],
                                        paths['model']['name'] + '.dom'))
        paths['hd']['sh'] = os.path.join(paths['hd']['out_folder'],
                                         paths['model']['name'] + '.sh')
        paths['hd']['so'] = os.path.join(paths['hd']['out_folder'],
                                         'libuserfuncs.so')
        paths['hd']['userfuncs'] = os.path.join(hd_path, 'gens', 'hs', 'src',
                                                'userfuncs.h')

        paths['hd']['plot'] = os.path.join(paths['hd']['out_folder'],
                                           'params_plot.txt')
        
        if self.use_workspace:
            hd_settings_prefix = workspace
        else:
            hd_settings_prefix = paths['hd']['hd']

        # hd paths:
        if self.use_pf_prefix:
            file_or_folder = self.device_conf_name + ".json"
        else:
            file_or_folder = "device_conf"
        paths['hd']['device_conf'] = (os.path
                                      .join(hd_settings_prefix,
                                            settings_folder, file_or_folder))

        if self.use_pf_prefix:
            file_or_folder = self.paths_name + ".json"
        else:
            file_or_folder = "paths"

        paths['hd']['paths'] = (os.path
                                .join(hd_settings_prefix,
                                      settings_folder, file_or_folder))

        # hs paths:
        paths['hs'] = {}

        paths['Workspace'] = workspace

        # traceFolder:
        tracerFolder = paths['TracerFolder']
        tracerFolder = self.fix_tilde_bug(tracerFolder, 'tracer', 'folder')
        paths['TracerFolder'] = tracerFolder

        # path to solver:
        paths['hs']['solver'] = os.path.join(tracerFolder,
                                             "hybridsolver", "bin", "HS")

        # path to hd at solver:
        paths['hs']['hd'] = os.path.join(tracerFolder,
                                         "hybriddomain")

        # hs settings:
        paths['hs']['settings'] = os.path.join(workspace, 'settings')
        
        # hs device_conf:
        paths['hs']['device_conf'] = os.path.join(paths['hs']['settings'],
                                                  'device_conf')
        # paths['hs']['device_conf'] = os.path.join(paths['hs']['hd'],
        #                                           'settings', 'device_conf')
        # hs paths:
        paths['hs']['paths'] = os.path.join(paths['hs']['settings'],
                                            'paths')
        # paths['hs']['paths'] = os.path.join(paths['hs']['hd'],
        #                                     'settings', 'paths')

        # path to project folder at server:
        paths['hs']['project_path_relative'] = (os.path
                                                .join('problems',
                                                      paths['model']['path']))
        paths['hs']['project_path_absolute'] = (os.path
                                                .join(workspace,
                                                      paths['hs']['project_path_relative']))
        # path to json at server:
        paths['hs']['json'] = (os.path
                               .join(paths['hs']['project_path_absolute'],
                                     paths['model']['json']))

        #  file at server:
        paths['hs']['out_folder'] = (os.path
                                     .join(paths['hs']['project_path_absolute'],
                                           paths['model']['out_folder']))

        # cpp file at server:
        paths['hs']['cpp'] = (os.path
                              .join(paths['hs']['out_folder'],
                                    paths['model']['name'] + '.cpp'))

        # dom file at server:
        paths['hs']['dom_bin'] = (os.path
                                  .join(paths['hs']['out_folder'],
                                        paths['model']['name'] + '.dom'))
        # sh file at server:
        paths['hs']['sh'] = (os.path
                             .join(paths['hs']['out_folder'],
                                   paths['model']['name'] + '.sh'))

        paths['hs']['postproc'] = os.path.join(tracerFolder,
                                               'hybriddomain',
                                               'solvers', 'hs',
                                               'postproc', 'video',
                                               'postprocessor.py')

        paths['hs']['plot'] = os.path.join(paths['hs']['out_folder'],
                                           'params_plot.txt')

    def fix_tilde_bug(self, path, where, name):
        
        '''Replace ``~/`` with ``/home/username``
        where ``username`` from self.connection.
        If ``self.connection`` not setup yet, return
        ``path`` (unchanged).'''
        
        try:
            connection = self.connection
            username = connection.username
        except AttributeError:
            if self.username is None:
                
                raise(BaseException("cannot fix tilde bug:"
                                    + " connection (username) not set"))
                '''
                # do not fix if connection (username) not set:
                logger.debug("cannot fix tilde bug:"
                             + " connection (username) not set")
                return(path)
                '''
            else:
                username = self.username

        # fix tilde bug:
        path = path.replace("~", "/home/" + username)
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
