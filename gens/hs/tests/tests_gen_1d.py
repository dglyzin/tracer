'''
hd$ python3 -m gens.hs.tests.tests_gen_1d -t project_folder \
-d device_conf_name -p paths_name \
-w workspace_folder_location -u username

where

   project path to folder, where .json file stored
         and it can be:

      either relative to hd:
      (ex: ``problems/1dTests/test_folder``)
      python3 -m gens.hs.tests.tests_gen_1d -t problems/1dTests/logistic_delays

      or absolute:
      (ex: )
      python3 -m gens.hs.tests.tests_gen_1d -t \
      ~/projects/lab/hybriddomain/problems/1dTests/logistic_delays

      or test_folder name
          where test_folder in ``hd/problems/1dTests``
      python3 -m gens.hs.tests.tests_gen_1d -t logistic_delays

   workspace_folder_location (optional) is path to folder
      where "problems" and "settings" folder lie.
      If no given, "problems" will be used from hd/problems,
      "settings" from hd/settings.
      This parameter used only at server (remotely).

   username used for interpetation of tilde (~) in pathes if
      connection file not used or not exist.

   paths_name (optional) is name of paths file in paths folder
      deffault is ``paths_hs_base``

   device_conf_name (optional) is name of device_conf file in
      device_conf folder deffault is ``default``

generaly for tests at client side use:
   python3 -m gens.hs.tests.tests_gen_1d -t logistic_delays -u username

   # or with undefault settings:
   python3 -m gens.hs.tests.tests_gen_1d -t logistic_delays -p paths_hs_base \
   -u username

for run from remoterun.py use:

   # go to hs_hd dirrectory, show it
   # and run source generator:
   command = ("cd " + hs_hd + " &&"
              + " pwd &&"
              + (" python3 "
                 + ("-m gens.hs.tests.tests_gen_%dd"
                    % dimention))
              + ' -t ' + hs_project_folder
              + ' -d ' + settings.device_conf_name
              + ' -p ' + settings.paths_name
              + ' -w ' + workspace
              + ' -u ' + connection.username)
'''
from gens.hs.gen_env.gen_dim import GenD1
from gens.hs.gen_main import Gen

from settings.settings_main import Settings
from envs.hs.model.model_main import ModelNet as Model

from tests.tests_common import get_model_for_tests
from tests.tests_common import to_file, test_cpp

import os
import sys


def get_gen_1d(model='problems/test1d_two_blocks0',
               device_conf='default'):
    settings = Settings()
    gen = Gen(model, settings, device_conf)
    return(gen)


def test_gen_1d(model='problems/test1d_two_blocks0',
                device_conf='default', paths_name='paths_hs_base',
                workspace=None, username=None):

    # model:
    if type(model) == str:
        oModel = Model()
        oModel.io.loadFromFile(model)
        model = oModel
    else:
        model = model

    print("model:")
    print(model.base.projectName)

    # settings:
    settings = Settings(model, None, device_conf, paths_name,
                        workspace=workspace, username=username)
    # settings.make_all_pathes(model)
    # settings.set_device_conf(device_conf)

    gen = Gen(model, settings)
    gen.gen_all()
    gen.save_all()
    return(gen)


def test_gen_1d_old(model="tests/test1d_two_blocks0.json"):
    gen = GenD1(model)
    gen.gen_cpp()
    gen.gen_arrays()
    
    # save cpp:
    name = os.path.basename(model)
    cppFileName = to_file(gen.cpp_out, name)

    # save dom txt:
    folderName = cppFileName.split('.')[0]
    domFileName = folderName + '_dom.txt'

    gen.filler.save_txt(domFileName)

    # save dom bin:
    binFileName = folderName + '_bin.dom'
    gen.filler.save_bin(binFileName)

    return(os.path.basename(cppFileName))


if __name__ == '__main__':

    '''
    
    '''

    if '-t' in sys.argv:
        test_idx = sys.argv.index('-t') + 1
        test_id = sys.argv[test_idx]
        if len(test_id.split(".")) > 1:
            raise(BaseException("tests_gen_1d -t parameter is"
                                + " a path (relative to hd or absolute)"
                                + "\n of folder, .json file contained in"))
        if len(test_id.split(os.path.sep)) > 1:
            test_name = test_id
        else:
            test_name = os.path.join('problems', '1dTests',
                                     sys.argv[test_idx])
    else:
        test_name = 'problems/1dTests/Brusselator1d'
        # test_name = 'problems/1dTests/two_blocks0_delays'

    if '-d' in sys.argv:
        device_conf_idx = sys.argv.index('-d') + 1
        device_conf_name = sys.argv[device_conf_idx]
    else:
        device_conf_name = "default"

    if '-p' in sys.argv:
        paths_idx = sys.argv.index('-p') + 1
        paths_name = sys.argv[paths_idx]
    else:
        paths_name = "paths_hs_base"
        
    if '-w' in sys.argv:
        workspace = sys.argv[sys.argv.index('-w') + 1]
    else:
        workspace = None

    if '-u' in sys.argv:
        username = sys.argv[sys.argv.index('-u') + 1]
    else:
        username = None
        
    test_gen_1d(test_name, device_conf_name, paths_name,
                workspace, username)
