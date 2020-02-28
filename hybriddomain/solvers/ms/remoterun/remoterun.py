import os
import sys
from hybriddomain.solvers.hs.remoterun.remoterun import Remoterun
from hybriddomain.solvers.ms.remoterun.io_routine import MSIORoutine
from hybriddomain.solvers.ms.remoterun.runner import MSRunner

from hybriddomain.settings.settings_main import Settings
from hybriddomain.envs.ms.model.model_main import ModelNet as Model

'''
# field:
pf$ ~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.ms.remoterun.remoterun as ts; ts.run()"  -conn_name connection_acchome.json -device_conf_name devices_acchome.json -paths_name connection_acchome.json -model ~/Documents/projects/projectsNew/lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test0 -steps 4 -type field -save_interval 3

# solver:
 ~/anaconda3/bin/./python3 -c "import hybriddomain.solvers.ms.remoterun.remoterun as ts; ts.run()"  -conn_name connection_acchome.json -device_conf_name devices_acchome.json -paths_name connection_acchome.json -model ~/Documents/projects/projectsNew/lab/hybriddomain/hybriddomain/gui/2d/web/model/data/physics/n-body/test0 -steps 4
'''


def remoteProjectRun(settings, dimension, notebook=None, model=None,
                     log_level_console="INFO", log_level_file="DEBUG",
                     remove_old=True, den='hd', sn='hs'):
    io = MSIORoutine(den=den, sn=sn)
    runner = MSRunner(den=den, sn=sn)

    remoterun = Remoterun(io, runner)
    remoterun.run(settings, dimension, notebook=notebook, model=model,
                  log_level_console=log_level_console,
                  log_level_file=log_level_file,
                  remove_old=remove_old)


def run():

    if '-model' in sys.argv:
        model_path = sys.argv[sys.argv.index('-model') + 1]
    else:
        raise(BaseException("-model needed"))

    if '-conn_name' in sys.argv:
        conn_name = sys.argv[sys.argv.index('-conn_name') + 1]
    else:
        raise(BaseException("-conn_name needed"))

    if '-device_conf_name' in sys.argv:
        device_conf_name = sys.argv[sys.argv.index('-device_conf_name') + 1]
    else:
        raise(BaseException("-device_conf_name needed"))

    if '-paths_name' in sys.argv:
        paths_name = sys.argv[sys.argv.index('-paths_name') + 1]
    else:
        raise(BaseException("-paths_name needed"))
    
    if '-steps' in sys.argv:
        steps = sys.argv[sys.argv.index('-steps') + 1]
    else:
        raise(BaseException("-steps needed"))

    if '-type' in sys.argv:
        solver_type = sys.argv[sys.argv.index('-type') + 1]
        if solver_type not in ["solver", "field"]:
            raise(BaseException("-type either 'solver' or 'field'"))
    else:
        solver_type = "solver"

    if '-start_from' in sys.argv:
        start_from = sys.argv[sys.argv.index('-start_from') + 1]
    else:
        start_from = None

    if '-save_interval' in sys.argv:
        save_interval = sys.argv[sys.argv.index('-save_interval') + 1]
        save_interval = save_interval
    else:
        save_interval = "3"

    model = Model()
    modelFileName = os.path.join("ms", model_path.split("data/")[-1])
    model.io.loadFromFile(modelFileName)
    settings = Settings(model, conn_name, device_conf_name, paths_name)
    settings.device_conf["steps"] = steps
    settings.device_conf["solver_type"] = solver_type
    settings.device_conf["start_from"] = start_from
    settings.device_conf["save_interval"] = save_interval

    dimension = 2
    settings.paths['hd']['project_path'] = model_path
    settings.paths['hd']['out_folder'] = model_path
    '''
    settings.paths['hs']['project_path_relative']
    hsr = settings.paths['hs']['project_path_relative']
    settings.paths['hs']['project_path_relative'] = hsr.split("data/")[-1]
    settings.paths['hs']['out_folder'] = settings.paths['hs']['project_path_absolute']
    '''
    print(settings.paths['hd'])
    print(settings.paths['hs'])
    remoteProjectRun(settings, dimension, notebook=None, model=model,
                     log_level_console="DEBUG")
