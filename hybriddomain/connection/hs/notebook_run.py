'''
DESCRIPTION:
# Run all from hybriddomain directory, whose parent's contained
# hybriddomain and hybridsolver.

# for test using file "/hybriddomain/tests/test2d_one_block0.json"

# for generate src for test params['fileName'] (see below):
   python3 -m hybriddomain.notebook_run -g
# files will be in params['outFileName']

# for run solver:
   python3 -m hybriddomain.notebook_run -r
'''
# from jsontobin import createBinaries
import os
import sys
import subprocess


def fill_params(json_file_name: str, test_folder='tests'):
    '''
    DESCRIPTION:
    Fill params dictionary for solver.

    INPUT:
    json_file_name - like test_1.json.

    TODO:
    # outFileName must be in ... 
    '''
    # current location (must be hybriddomain):
    current = os.getcwd()
    
    # (must be folder, where hybriddomain and hybridsolver):
    tracer_folder = os.path.dirname(current)

    # FOR where project source files will be stored:
    # example for test_1.json it will be:
    # tracer_folder + "projects_folder/test_1/test_1.*:
    json_name_only = json_file_name.split('.')[0]

    # project folder for current json test:
    project_folder = os.path.join(tracer_folder, 'project_folder',
                                  json_name_only)
    out_files_path = os.path.join(project_folder, json_name_only)
    # example: out_files_path = tracer_folder/test_1/test_1.*
 
    # create folder with name json_name_only
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)
    # END FOR

    # path to test_1.json:
    json_file_path = os.path.join(tracer_folder, 'hybriddomain',
                                  test_folder, json_file_name)

    params = {
        'affinity': None,
        'cont': None,
        'fileName': json_file_path,
        'finish': None,
        'jobId': None,
        'mpimap': None,
        'nocppgen': None,
        'nodes': 'dnode1',
        'nortpng': None,
        'outFileName': out_files_path,
        'partition': None,
        'tracerFolder': tracer_folder
    }

    # params['continueFileName']
    
    return(params)


def create_video(params):
    plotIdx = 1
    command = ("avconv -r 5 -loglevel panic -i "
               + params['outFileName']
               + "-plot"+str(plotIdx)+".png -b:v 1000k "
               + params['outFileName']+"-plot"+str(plotIdx)+".mp4")
    print(command)
    # cmd = command.split()
    # run_cmd(cmd)


def run_solver(params):
    script_name = params['outFileName'] + '.sh'
    cmd = ['sh', script_name]
    run_cmd(cmd)


# def compile_cpp(params):
    
def generate_files(params):
    '''
    DESCRIPTION:
    
    INPUT:
    in tracerFolder hybriddomain and hybridsolver must exist.
    
    OUT:
    Will be in params['outFileName'].
    '''

    cmd = ['python2', os.path.join(params['tracerFolder'],
                                   'hybriddomain/jsontobin.py'),
           params['fileName'],
           params['tracerFolder']]

    if params['outFileName'] is not None:
        cmd.extend(['-outFileName', params['outFileName']])
    if params['cont'] is not None:
        cmd.extend(['-cont', params['cont']])
    if params['jobId'] is not None:
        cmd.extend(['-jobId', params['jobId']])
    if params['finish'] is not None:
        cmd.extend(['-finish', params['finish']])
    if params['nortpng'] is not None:
        cmd.extend(['-nortpng'])
    if params['nocppgen'] is not None:
        cmd.extend(['-nocppgen'])
    
    run_cmd(cmd)
    # createBinaries(params)


def run_cmd(cmd, _stderr=None):
    # logger.debug("cmd = %s" % str(cmd))
    print(cmd)
    '''
    stdout and stderr PIPE means
    that new child stream will be created
    so standart output will be unused.
    See:
    https://docs.python.org/2.7/library/subprocess.html#frequently-used-arguments
    https://docs.python.org/2.7/library/subprocess.html#subprocess.Popen.communicate
    '''
    
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()

    if (err is not None and len(err) > 0
        and _stderr is None):
        raise(GccException(err))
    if _stderr is not None:
        print("out")
        print(out)
        print("err")
        print(err)
    return(out)
    

class GccException(Exception):
    '''
    DESCRIPTION:
    For cathing error of gcc.
    For tests cases in tester.py.
    '''
    def __init__(self, err):
        self.err = err


if __name__ == '__main__':

    file_name = 'test2d_one_block1.json'
    test_folder = 'tests/2dTests'
    params = fill_params(file_name, test_folder)
    print('file_name:\n', file_name)

    if '-g' in sys.argv:
        generate_files(params)
    elif '-r' in sys.argv:
        run_solver(params)
    elif '-v':
        create_video(params)
    else:
        print(('arguments must be either'
               + ' -g (generate_files)'
               + ' or -r (run_solver)'))
