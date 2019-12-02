from hybriddomain.envs.hs.model.model_main import ModelNet as Model

import numpy as np
import matplotlib.pyplot as plt


def test_extract_results_paths(model):
    model.io.loadFromFile("problems/1dTests/2vars")
    # settings = Settings(model, "conn_cluster1",
    #                     "default", "paths_hs_cluster1")
    model.io.loadFromFile("problems/1dTests/2vars")
    print("Plots and Results:")
    print(model.project_path)
    print(model.plots_paths)
    print(model.results_paths)
    return(model)


if __name__ == "__main__":
    model = Model()
    model = test_extract_results_paths(model)

    print("\nresults arrays:")
    model.readResults()
    firstname = model.results[0]["Name"]
    times = model.results_arrays[firstname]["timevalues"]
    results = model.results_arrays[firstname]["resvalues"]
    
    print("\ntimes:")
    print(times)
    print("\nresults[0]")
    print(results[0])

    print("\nresults arrays:")
    model.readResults(result_format=0)
    firstname = model.results[0]["Name"]
    times = model.results_arrays["timevalues"]
    results = model.results_arrays["resvalues"][firstname]

    print("\ntimes:")
    print(times)
    print("\nresults[0][0]")
    print(results[0][0])
    
    '''
    print("\nresults.keys():")
    print(results.keys())

    # first name:
    name = list(results.keys())[0]

    var = 0
    time = times[0]
    data = np.array([results[name][var][time] for time in times],
                    dtype=np.float32)
    print(data)
    plt.imshow(data.T)
    plt.show()
    # plt.plot(results[name][var][time])
    # plt.show()
    
    print(results[name][var][time])
    '''
