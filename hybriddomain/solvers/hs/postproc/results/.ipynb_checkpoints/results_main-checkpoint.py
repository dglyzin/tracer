import os
import re
import numpy as np
from functools import reduce


class ResultPostprocNet():
    '''
    Usage1:
        # init
        from hybriddomain.solvers.hs.postproc.results.results_main import ResultPostprocNet as ResultPostproc
        result_postproc = ResultPostproc(os.path.join(hd_dir,"problems", model_path))
        
        # parametrisation:
        results_params = {}
        in loop:
           result_postproc.extract_out(param_idx, results_params)
           result_postproc.rename_out(param_idx)
        
        # convert to arrays:
        progress_array = ProgressNotebook(params_count*vars_count, prefix='file')
        times, results_param_arrays = result_postproc.out_to_array(results_params, progress_array)

        # remove files
        result_postproc.remove_out()
    Usage2:
        from hybriddomain.solvers.hs.postproc.results.results_main import ResultPostprocNet as ResultPostproc
        result_postproc = ResultPostproc(project_folder)
        # or result_postproc = ResultPostproc("", hd_out_folder)

        # or use result_postproc.get_results_files()
        plots_names = [plot["Name"] for plot in model.plots]
        filenames_plot = [filename for filename in filenames
                          if filename.endswith('mp4')]
        model.plots_paths = (result_postproc
                       .set_paths(filenames_plot, plots_names))
    Usage3:
        from hybriddomain.solvers.hs.postproc.results.results_main import ResultPostprocNet as ResultPostproc
        result_postproc = ResultPostproc(project_folder)
        result_postproc.set_results_arrays(self, names=names,
                                           result_format=result_format,
                                           progress=progress)
    '''

    def __init__(self, model_dir, hd_out_folder=None):

        '''``self.replacer_id`` used for renaming of ``.out``
        files in order to prevent rewriting in parametrization'''
        
        self.model_dir = model_dir
        if hd_out_folder is not None:
            self.hd_out_folder = hd_out_folder
        else:
            self.hd_out_folder = os.path.join(self.model_dir, "out")
        # print("self.hd_out_folder:")
        # print(self.hd_out_folder)
        # print(os.listdir(self.hd_out_folder))
        # self.model_path = model_path
        self.replacer_id = "_seq"
        
        self.common_shape = None

    def get_video(self, model, plot_name, plot_idx=0):

        '''Return string that can be used for:
        display(HTML(str_video))'''

        plot_file_name = model.plots_paths[plot_name][plot_idx]
        str_video = '''
        <script>
        </script>

        <video controls>
        '''
        str_video += (('<source src="%s" type="video/mp4">'
                       + '<p>Your browser doesnt support HTML5 video.'
                       + 'Here is a <a href="%s">')
                      % (plot_file_name, plot_file_name)
                      + 'link to the video</a></p>')
        str_video += '</video>'
        return(str_video)

    def set_results_arrays(self, model, names=[],
                           result_format=1, progress=None):
        '''
        Extract mp4/out pathes to model.{plots_/results_}pathes,
        output arrays to model.results_arrays
        
        -- ``result_format`` -
        if 0 then result will be:
         res["timevalues"] = [0.0, 0.1, 0.2, 0.3, ... ]
        
         # data acces for 1d or 2d:
         model.results_arrays['resvalues']['name0'][filenumber or var][time]
         # for special case for several vars under one time (spec_svuot):
         model.results_arrays['resvalues']['u'][filenumber][time][var]

        if 1 then:
         res[name]["timevalues"] = [0.0, 0.1, 0.2, 0.3, ... ]

        # data access for 1d:
         first_30_res = model.results_arrays['u']['resvalues'][time][filenumber or var][:30]
                        
        # data access for 2d in that case:
        time = model.results_arrays['name0']['timevalues'][3]
        res = model.results_arrays['name0']['resvalues'][time][filenumber or var]
        plt.imshow(res)
        
        # for special case for several vars under one time (spec_svuot):
        # if bijection between names and files:
        first_30_res = model.results_arrays[result_name]['resvalues'][time][var][:30]
        # else (in case of parametrization):
        first_30_res = model.results_arrays[result_name]['resvalues'][filenumber][time][var][:30]
        
        '''
        if "results_paths" not in dir(model):
            '''
            raise(BaseException(
                "no ``model.results_paths`` available."
                + "\nUse ``remoterun`` for generating reuslts."
                + "\nOr use ``set_settings`` "
                + "(for ``hd_out_folder`` path),"
                + "\n if they had alredy been downloaded"
                + "\nOr just specify ``hd_out_folder``"))
            '''

            # fill self.results_paths:
            self.get_results_filespaths(model)
        elif model.results_paths == {}:
            # refill self.results_paths:
            self.get_results_filespaths(model)

        # check if there is bijection between names and files:
        self.seq = any([len(model.results_paths[name]) > 1
                        for name in model.results_paths])

        # extract data from paths as strings:
        if len(names) > 0:
            results = dict([(name, model.results_paths[name])
                            for name in names])
        else:
            # print("model.results_paths:")
            # print(model.results_paths)
            results = model.results_paths

        names_strs = self.extract_out_from_paths(results)
        
        # print("names_strs:")
        # print(names_strs)
        
        # convert strings to arrays:
        times, names_arrays = (self
                               .out_to_array(names_strs, progress))
        # print("times orig:")
        # print(times)
        res = {}
        
        for name in names_arrays:
            res[name] = {}
            res[name]["timevaluesarray"] = np.array(times[name],
                                                    dtype=np.float32)
            res[name]["timevalues"] = times[name]
        
        if result_format == 1:

            # for get shape of all data:
            if self.common_shape is None:
                print("no results")
                return({})
            common_shape = self.common_shape
            # firstname = list(results.keys())[0]
            # firstvar = 0
            # common_shape = names_arrays[firstname][firstvar][0].shape
            
            common_dim = len(common_shape)
            
            # for checking special case for several vars under one time
            self.spec_svuot = ((model.dimension == 1 and common_dim == 2)
                               or (model.dimension == 2 and common_dim == 3))
            
            for name in names_arrays:
                res[name]["resvalues"] = {}
                # print("times:")
                # print(times)

                if self.spec_svuot:
                    # for special case for several vars under one time

                    # print("case when all vars inside times")
                    # case when all vars inside times:
                    # (ex 1d: (0.0, array([ [ ... ], [ ... ] ])))
                    # (ex 2d: (0,0, array([ [[ ... ]], [[ ... ]] ])))
                    # print("names_arrays[name]:")
                    # print(names_arrays[name])

                    if not self.seq:
                        '''# data access for 1d in that case:
                        first_30_res = model.results_arrays[result_name]['resvalues'][time][var][:30]
                        '''
                        res[name]["resvalues"] = names_arrays[name][0]
                    else:
                        '''# data access for 1d in that case:
                        first_30_res = model.results_arrays[result_name]['resvalues'][filenumber][time][var][:30]
                        '''
                        res[name]["resvalues"] = names_arrays[name]
                    # for filenumber in names_arrays[name]:
                    #     vars = range(len(names_arrays[name][filenumber][0]))
                else:
                    for idxt in times[name]:
                        # print("case when all vars inside files")
                        # map: [var][time] -> [time][var]:
                        '''
                        a1 = np.ones((3))
                        a2 = np.ones((3))
                        np.concatenate((a1.reshape((3,1)),a2.reshape((3,1))),axis=1)
                        a1 = np.ones((3,3))
                        a2 = np.ones((3,3))
                        np.concatenate((a1.reshape((3,3,1)),a2.reshape((3,3,1))),axis=2)
                        '''
                        # FOR unite differ vars for fixed time:
                        # print("vars:")
                        # print([var for var in names_arrays[name]])
                        # print("names_arrays[name][var][idxt]")
                        # print("times keys:")
                        # print(names_arrays[name][0].keys())
                        # print("names_arrays[name][0][0.0]:")
                        # print(names_arrays[name][0][0.0])
                        # print("common_shape:")
                        # print(common_shape)
                        vars_data = [
                            names_arrays[name][var][idxt].reshape(
                                common_shape+(1,))
                            for var in names_arrays[name]]

                        '''# data access for 1d in that case:
                        first_30_res = model.results_arrays['u']['resvalues'][time][filenumber or var][:30]
                        '''
                        '''# data access for 2d in that case:
                        time = model.results_arrays['name0']['timevalues'][3]
                        res = model.results_arrays['name0']['resvalues'][time][filenumber or var]
                        plt.imshow(res)
                        '''
                        res[name]["resvalues"][idxt] = np.concatenate(vars_data,
                                                                      axis=common_dim).T
                        # END FOR

        else:
            '''# data acces for 1d or 2d:
            model.results_arrays['resvalues']['name0'][filenumber or var][time]
            # for special case for several vars under one time (spec_svuot):
            model.results_arrays['resvalues']['u'][filenumber][time][var]
            '''            
            res["resvalues"] = names_arrays

        model.results_arrays = res
        return(res)

    def get_results_filespaths(self, model):
        
        '''Extract downloaded from solver out/mp4 filepaths
        to model.results_paths/model.plots_paths.'''

        hd_out_folder = self.hd_out_folder

        if os.path.exists(hd_out_folder):
            plots_names = [plot["Name"] for plot in model.plots]
            results_names = [result["Name"] for result in model.results]

            result_files = self.get_results_files()
            # print("result_files:")
            # print(result_files)

            filenames_plot, filenames_result = result_files
            model.plots_paths = (self
                                 .set_paths(filenames_plot, plots_names))
            model.results_paths = (self
                                   .set_paths(filenames_result,
                                              results_names))

    def get_results_files(self):

        '''Get downloaded from solver out/mp4 files '''

        filenames_plot = []
        filenames_result = []
        # print("self.hd_out_folder:")
        # print(self.hd_out_folder)
        # print("sorted(os.listdir(self.hd_out_folder)):")
        # print(sorted(os.listdir(self.hd_out_folder)))

        for filename in sorted(os.listdir(self.hd_out_folder)):
            if filename.endswith('mp4'):
                filenames_plot.append(filename)
            elif(filename.endswith('out')):
                filenames_result.append(filename)
        return(filenames_plot, filenames_result)
                   
    def set_paths(self, filenames, datanames):
        '''
        Factorize filenames at datanames depending on
        filename contained dataname.
        Return dict[(name, [filename for each filename in filenames
        if name in filename])].
        '''
        data = {}
        for name in datanames:
            idxs_bool = list(map(lambda filename: name in filename,
                                 filenames))
            if True in idxs_bool:
                mapped = [os.path.join(self.hd_out_folder, filename)
                          for idx, filename in enumerate(filenames)
                          if idxs_bool[idx]]
                data[name] = mapped
        return(data)

    def get_params_results(self, progress):
        
        def get_idxs(filepath):
            filename = os.path.basename(filepath)
            res_seq = re.search("_seq(?P<idx>\d+)", filename)
            res = int(res_seq.groupdict()["idx"])
            # res_val = re.search("-value(?P<idx>\d+)", filename)
            # res = (int(res_seq.groupdict()["idx"]),
            #        int(res_val.groupdict()["idx"]))
            return(res)

        # bouts = list(map(get_idxs, outs))
        
        out_dir = os.path.join(self.model_dir, "out")
        listdir = os.listdir(out_dir)
        replacer_id = self.replacer_id

        outs = [os.path.join(out_dir, file_name)
                for file_name in listdir
                if ('.out' in file_name) and (replacer_id in file_name)]
        outs.sort(key=lambda elm: get_idxs(elm))
        
        def succ(acc, filename):
            seq_idx = get_idxs(filename)
            if seq_idx not in acc:
                with open(filename) as f:
                    seq_val_data = f.read()
                acc[seq_idx] = seq_val_data
            '''
            # TODO: for -values or for -blocks
            seq_idx, val_idx = get_idxs(filename)
            
            if seq_idx not in acc:
                acc[seq_idx] = {}
            
            with open(filename) as f:
                seq_val_data = f.read()
            acc[seq_idx][val_idx] = seq_val_data
            '''
            return(acc)
        res_strings = reduce(succ, outs, {})

        self.results_param_strings = res_strings

        '''
        # reinit progress steps:
        if progress is not None:
            progress.set_steps(len(outs))
        '''
        # convert to arrays:
        times, res_arrays = self.out_to_array(res_strings, progress)
    
        self.times = times
        
        # check if there is bijection between names and files:
        self.seq = any([len(res_arrays[name]) > 1
                        for name in res_arrays])
        self.results_param_arrays = {}
        for param in res_arrays:
        
            if not self.seq:
                '''# data access for 1d in that case:
                first_30_res = results_param_arrays[seq_number][time][var][:30]
                '''
                self.results_param_arrays[param] = res_arrays[param][0]
            else:
                '''# data access for 1d in that case:
                first_30_res = results_param_arrays[seq_number][filenumber][time][var][:30]
                '''
                self.results_param_arrays[param] = res_arrays[param]
        # self.results_param_arrays = res_arrays
        
        return((times, self.results_param_arrays))

    def out_to_array(self, results_params, progress=None):

        '''Convert strings with data from ``results_params[param]``
        to lists.

        Inputs:

        - ``results_params`` -- dict with values
        (like: "0.3133: [0.12, 0.13, ..., 3.1]"
         or: ["0.3133: [0.12, 0.13, ..., 3.1]"]
         or: {"key": "0.3133: [0.12, 0.13, ..., 3.1]"})

        - ``progress`` -- ProgressNotebook instance.

        Return:

        - ``results_param_arrays`` -- dict
        (like: results_param_arrays[param][var][time]
                = [0.12, 0.13, ..., 3.1])
        '''

        results_param_arrays = {}
        times = {}

        def gen(result):
            for key in result:
                step_0_0 = result[key].replace('...,', "")
                step_0_1 = re.subn(r'\[\s+', "[", step_0_0)[0]
                step_0 = re.subn(r'\.\s+', ".0,", step_0_1)[0]
                step_1 = re.subn(r'\s+', ",", step_0)[0]
                step_2 = step_1.replace('.]', '.0]')
                step_3 = step_2.replace('[,', '[')
                step_4 = step_3.replace("nan", "None")
                step_5 = eval(step_4)
                step_6 = np.array(step_5, dtype=np.float32)
                yield((key, step_6))

        steps = 0
            
        # reinit progress steps:
        if progress is not None:
            progress.set_steps(len(results_params))

        for param in results_params:
            result_t = []

            # TODO: only dict for all
            if type(results_params[param]) == dict:
                # if vars data stored like a dict,
                # convert to generator object:
                vars_keys = list(results_params[param].keys())
                vars_keys.sort()
                data_list = (results_params[param][var_id]
                             for var_id in vars_keys)
            elif type(results_params[param]) == str:
                data_list = [results_params[param]]
            else:
                # default is list:
                data_list = results_params[param]

            # reinit progress steps:
            if progress is not None:
                progress.set_steps(progress.get_steps()+len(data_list)-1)

            for var, data in enumerate(data_list):

                if param not in results_param_arrays:
                    results_param_arrays[param] = {}

                try:
                    lines = data.split('\n')
                    result = {}

                    # separate time:
                    for line in lines:
                        if ':' in line:
                            key, val = line.split(':')
                            result[key] = val[1:]
                        else:
                            val = line
                            result[key] += val
                    # parse arrays:
                    result_t = [(float(key), val) for key, val in gen(result)]
                    # print("result_t:")
                    # print(result_t)
                    self.result_t = result_t

                    # collect common_shape from some array
                    if self.common_shape is None:
                        try:
                            self.common_shape = result_t[0][1].shape
                        except:
                            pass
                
                except:
                    
                    results_param_arrays[param][var] = None
                    continue

                results_param_arrays[param][var] = dict(result_t)
                steps += 1
                if progress is not None:
                    progress.succ(steps)
                # print(steps)
            times[param] = [key[0] for key in result_t]

        self.results_param_arrays = results_param_arrays
        # result_x = np.array([result_t[key] for key in result_t]).T
        return(times, results_param_arrays)

    def remove_out(self):
        
        '''Clear ``.out`` and ``.mp4`` files from out folder.'''

        out_dir = os.path.join(self.model_dir, "out")
        # out_dir = os.path.join(self.hd_dir, 'problems',
        #                        self.model_path, "out")
        listdir = os.listdir(out_dir)

        outs = [os.path.join(out_dir, file_name)
                for file_name in listdir
                if '.out' in file_name]

        mp4 = [os.path.join(out_dir, file_name) for file_name in listdir
               if 'mp4' in file_name]

        for out in outs:
            os.remove(out)
            print(os.path.basename(out), "removed")

        for video in mp4:
            os.remove(video)
            print(os.path.basename(video), "removed")

    def extract_out(self, param_idx, data):

        '''extract data from ``.out`` files to
        ``data[param_idx]``'''

        out_dir = os.path.join(self.model_dir, "out")
        # out_dir = os.path.join(self.hd_dir, 'problems',
        #                        self.model_path, "out")
        listdir = os.listdir(out_dir)

        replacer_id = self.replacer_id
        
        outs = [os.path.join(out_dir, file_name)
                for file_name in listdir
                if ('.out' in file_name) and (replacer_id not in file_name)]
        # print(outs)

        data[param_idx] = []
        for out in outs:
            param_data = "failure"
            with open(out) as f:
                param_data = f.read()
            data[param_idx].append(param_data)
        # return(data)

    def extract_out_from_paths(self, data_paths):

        '''Extract data str from names/paths dict,
        returned with ``set_paths`` or ``get_results_filespaths``func.'''

        data_str = {}
        for name in data_paths:
            data_str[name] = []
            for var, filepath in enumerate(data_paths[name]):
                param_data = "failure"
                with open(filepath) as f:
                    param_data = f.read()
                data_str[name].append(param_data)
        return(data_str)

    def rename_out(self, param_idx):

        '''rename ``.out`` and ``.mp4`` files in order to
        prevent their revriting.
        (see also ``self.replacer_id`` in ``self.__init__``)'''

        out_dir = os.path.join(self.model_dir, "out")
        # out_dir = os.path.join(self.hd_dir, 'problems',
        #                        self.model_path, "out")
        listdir = os.listdir(out_dir)

        replacer_id = self.replacer_id
        replacer = replacer_id+str(param_idx)

        outs = [os.path.join(out_dir, file_name)
                for file_name in listdir
                if ('.out' in file_name) and (replacer_id not in file_name)]
        new_outs = [out.replace(".out", replacer+".out")
                    for out in outs]

        mp4 = [os.path.join(out_dir, file_name) for file_name in listdir
               if 'mp4' in file_name and (replacer_id not in file_name)]
        new_mp4 = [file_name.replace(".mp4", replacer+".mp4")
                   for file_name in mp4]

        for num, out in enumerate(outs):
            os.rename(out, new_outs[num])

        for num, file_name in enumerate(mp4):
            os.rename(file_name, new_mp4[num])


def test_get_params(model_dir):
    import hybriddomain.solvers.hs.remoterun.progresses.progress_cmd as pcmd
    
    rp = ResultPostprocNet(model_dir)
    
    # set progress with arbitrary value:
    # (it will be rewrited inside get_params_results)
    p = pcmd.ProgressCmd(1)
 
    rp.get_params_results(p)
    return(rp)
