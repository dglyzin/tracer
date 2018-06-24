import os
import json
import shutil


settings_folder = 'settings'
conn_folder = os.path.join(settings_folder, 'conn')
device_conf_folder = os.path.join(settings_folder, 'device_conf')
pathes_folder = os.path.join(settings_folder, 'pathes')


class Settings():
    def __init__(self):

        '''Extract all settings in:
        self.conn, self.device_conf, self.pathes
        
        Each file will be key in according settings:
           settings/conn/conn_base.json -> self.conn['conn_base']'''

        def get_data(sfolder, sfile):
            # print(sfile)
            with open(os.path.join(sfolder, sfile)) as f:
                data = json.loads(f.read())
            return(data)

        settings = [dict([(sfile.split('.')[0],
                           get_data(sfolder, sfile))
                          for sfile in os.listdir(sfolder)
                          if sfile.split('.')[-1] == 'json'])
                    for sfolder in
                    [conn_folder, device_conf_folder, pathes_folder]]

        self.conn, self.device_conf, self.pathes = settings

    def make_all_pathes(self, model):

        '''Creating all pathes for problem'''

        hd_path = os.getcwd()
        pathes = self.pathes

        # modlel pathes:
        pathes['model'] = {}
        pathes['model']['path'] = model.project_path
        pathes['model']['name'] = model.project_name
        pathes['model']['out_folder'] = 'out'

        # hd pathes:
        pathes['hd'] = {}
        pathes['hd']['out_folder'] = (os.path
                                      .join(hd_path, 'problems',
                                            pathes['model']['path'],
                                            pathes['model']['out_folder']))
        pathes['hd']['cpp'] = (os.path
                               .join(pathes['hd']['out_folder'],
                                     pathes['model']['name'] + '.cpp'))
        pathes['hd']['dom_txt'] = (os.path
                                   .join(pathes['hd']['out_folder'],
                                         pathes['model']['name'] + '_dom.txt'))
        pathes['hd']['dom_bin'] = (os.path
                                   .join(pathes['hd']['out_folder'],
                                         pathes['model']['name'] + '_dom.bin'))
        pathes['hd']['sh'] = os.path.join(pathes['hd']['out_folder'],
                                          pathes['model']['name'] + '.sh')
        pathes['hd']['so'] = os.path.join(pathes['hd']['out_folder'],
                                          'libuserfuncs.so')
        pathes['hd']['userfuncs'] = os.path.join(hd_path, 'gens', 'hs', 'src',
                                                 'userfuncs.h')

        # hs pathes:
        pathes['hs'] = {}

        # projects folder at server:
        workspace = pathes['pathes_hs_base']['Workspace']
        
        # path to project folder at server:
        pathes['hs']['project_path'] = os.path.join(workspace,
                                                    pathes['model']['path'])
        # dom file at server:
        pathes['hs']['dom_bin'] = (os.path
                                   .join(pathes['hs']['project_path'],
                                         pathes['model']['out_folder'],
                                         pathes['model']['name'] + '_dom.bin'))

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
