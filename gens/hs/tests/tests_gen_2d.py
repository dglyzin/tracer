'''
hd$ python3 -m gens.hs.tests.tests_gen_2d -t project_folder \
-d device_conf_name -p paths_name \
-w workspace_folder_location -u username

where

   project folder is folder, where .json file stored
         and it can be:

      either relative to hd:
      (ex: ``problems/2dTests/test_folder``)
      python3 -m gens.hs.tests.tests_gen_2d -t \
      problems/2dTests/heat_block_2_ics_other -d ics_other

      or absolute:
      (ex: )
      python3 -m gens.hs.tests.tests_gen_2d -t \
      ~/projects/lab/hybriddomain/problems/2dTests/heat_block_2_ics_other -d ics_other

      or test_folder name
      where test_folder in ``hd/problems/2dTests``
      python3 -m gens.hs.tests.tests_gen_2d -t heat_block_2_ics_other -d ics_other

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

generaly for tests at client side use::

   python3 -m gens.hs.tests.tests_gen_2d -t heat_block_2_ics_other -d ics_other -u username

   # or with undefault settings

   python3 -m gens.hs.tests.tests_gen_2d -t heat_block_2_ics_other \
   -d ics_other -p paths_hs_base -u username

for run from remoterun.py use::

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

from gens.hs.gen_env.gen_dim import GenD2
from gens.hs.gen_main import Gen

from settings.settings_main import Settings
from envs.hs.model.model_main import ModelNet as Model

from tests.tests_common import get_model_for_tests
from tests.tests_common import to_file, test_cpp

import os
import sys


def test_gen_2d(model='problems/2dTests/tests_2d_two_blocks0',
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


def test_gen_dim_2d(model=('problems/2dTests/tests_2d_two_blocks0')):
    
    # model:
    if type(model) == str:
        oModel = Model()
        oModel.io.loadFromFile(model)
        model = oModel
    else:
        model = model

    class TmpNet():
        pass
    tmp_net = TmpNet()
    tmp_net.model = model

    gen_dim = GenD2(tmp_net)
    gen_dim.gen_cpp()
    gen_dim.gen_dom()
    
    # print("cpp_out")
    # print(gen_dim.cpp_out)

    print("\nnamesAndNumbers:")
    print(gen_dim.namesAndNumbers)

    print("\nfucntionMaps:")
    print(gen_dim.functionMaps)

    return(gen_dim)


if __name__ == '__main__':

    if '-t' in sys.argv:
        test_idx = sys.argv.index('-t') + 1
        test_id = sys.argv[test_idx]
        if len(test_id.split(".")) > 1:
            raise(BaseException("tests_gen_2d -t parameter is"
                                + " a path (relative to hd or absolute)"
                                + "\n of folder, .json file contained in"))
        if len(test_id.split(os.path.sep)) > 1:
            test_name = test_id
        else:
            test_name = os.path.join('problems', '2dTests',
                                     sys.argv[test_idx])
    else:
        test_name = 'problems/2dTests/tests_2d_two_blocks0'

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

    test_gen_2d(test_name, device_conf_name, paths_name,
                workspace, username)
    
    # test_gen_2d()
    # test_gen_dim_2d()
