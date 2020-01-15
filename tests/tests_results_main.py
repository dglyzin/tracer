# hd$ ~/anaconda3/bin/./python3 -m tests.tests_results_main
from hybriddomain.envs.hs.model.model_main import ModelNet as Model
from hybriddomain.solvers.hs.remoterun.progresses.progress_cmd import ProgressCmd
import os
hd_tests = "tests"


def init_model(result_format, model_local_path):
    model = Model()
    path = os.path.join(hd_tests, model_local_path)
    model.io.loadFromFile(path)

    progress_cmd = ProgressCmd(1)

    model.readResults(result_format=result_format,
                      progress=progress_cmd)
    return(model)


def test_rf1_1d():

    '''Test 'result_format=1' (TRAC-11):
    # data acces for 1d:
    model.results_arrays['u']['resvalues'][time][filenumber or var]
    '''
    
    print("test_rf1_1d:", end="\n")
    result_format = 1
    model = init_model(result_format,
                       "problems/1dTests/Ginzburg_Landau_params")
    filenumber = 0
    time = 0
    result = model.results_arrays['u']['resvalues'][time][filenumber]
    print("done;")

    return(result)


def test_rf1_2d():

    '''Test 'result_format=1' (TRAC-11):
    # data acces for 2d:
    model.results_arrays['name0']['resvalues'][time][filenumber or var]
    '''
    
    print("test_rf1_2d:", end="\n")
    result_format = 1
    model = init_model(result_format,
                       "problems/2dTests/heat_block_2_ics_other_offsets")
    filenumber = 0
    time = 0
    result = model.results_arrays['name0']['resvalues'][time][filenumber]
    print("done;")

    return(result)


def test_rf0_2d():

    '''Test 'result_format=0':
    # data acces for 1d or 2d:
    model.results_arrays['resvalues']['name0'][filenumber or var][time]
    '''
    
    print("test_rf0_2d:", end="\n")
    result_format = 0
    model = init_model(result_format,
                       "problems/2dTests/heat_block_2_ics_other_offsets")
    filenumber = 0
    time = 0
    result = model.results_arrays['resvalues']['name0'][filenumber][time]
    print("done;")

    return(result)


def test_rf0_1d():

    '''Test 'result_format=0':
    # data acces for 1d or 2d:
    model.results_arrays['resvalues']['name0'][filenumber or var][time]
    '''
    
    print("test_rf0_1d:", end="\n")
    result_format = 0
    model = init_model(result_format,
                       "problems/1dTests/Ginzburg_Landau_params")

    filenumber = 0
    time = 0
    result = model.results_arrays['resvalues']['u'][filenumber][time]
    print("done;")

    return(result)


def test_rf0_1d_svuot():
    
    '''Test 'result_format=0' for special case
    (TRAC-22) for several vars under one time (spec_svuot):
    model.results_arrays['resvalues']['u'][filenumber][time][var]'''

    print("test_rf0_1d_svuot:", end="\n")

    result_format = 0
    model = init_model(result_format,
                       "problems/1dTests/Ginzburg_Landau")
    filenumber = 0
    time = 0
    var = 0
    result = model.results_arrays['resvalues']['u'][filenumber][time][var]
    var = 1
    result = model.results_arrays['resvalues']['u'][filenumber][time][var]
    print("done;")
    return(result)


def test_rf1_1d_svuot():
    
    '''Test 'result_format=1' (TRAC-11) for special case
    (TRAC-22) for several vars under one time (spec_svuot):
    # if bijection between names and files:
    model.results_arrays[result_name]['resvalues'][filenumber][time][var]
    # else (in case of parametrization):
    model.results_arrays[result_name]['resvalues'][time][var]
    '''
    
    print("test_rf1_1d_svuot:", end="\n")

    result_format = 1
    model = init_model(result_format,
                       "problems/1dTests/Ginzburg_Landau")
    # filenumber = 0
    time = 0
    var = 0
    result = model.results_arrays['u']['resvalues'][time][var]
    # result = model.results_arrays['u']['resvalues'][filenumber][time][var]
    var = 1
    result = model.results_arrays['u']['resvalues'][time][var]
    print("done;")

    return(result)


def test_rf1_1d_svuot_seq():
    
    '''Test 'result_format=1' (TRAC-11) for special case
    (TRAC-22) for several vars under one time (spec_svuot):
    # if bijection between names and files:
    model.results_arrays[result_name]['resvalues'][filenumber][time][var]
    # else (in case of parametrization):
    model.results_arrays[result_name]['resvalues'][time][var]
    '''
    
    print("test_rf1_1d_svuot_seq:", end="\n")

    result_format = 1
    model = init_model(result_format,
                       "problems/1dTests/Ginzburg_Landau_params_svuot")
    filenumber = 0
    time = 0
    var = 0
    result = model.results_arrays['u']['resvalues'][filenumber][time][var]
    var = 1
    result = model.results_arrays['u']['resvalues'][filenumber][time][var]
    print("done;")

    return(result)


if __name__ == "__main__":

    test_rf0_2d()
    test_rf1_1d()
    
    test_rf0_2d()
    test_rf0_1d()
    
    test_rf0_1d_svuot()
    test_rf1_1d_svuot()
    test_rf1_1d_svuot_seq()
    print("Done")
