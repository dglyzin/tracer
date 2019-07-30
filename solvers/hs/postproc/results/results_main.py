import os
import re


class ResultPostprocNet():

    def __init__(self, hd_dir, model_path):

        '''``self.replacer_id`` used for renaming of ``.out``
        files in order to prevent rewriting in parametrization'''

        self.hd_dir = hd_dir
        self.model_path = model_path
        self.replacer_id = "_seq"

    def out_to_array(self, results_params, progress=None):

        '''Convert strings with data from ``results_params[param]``
        to lists.

        Inputs:

        - ``results_params`` -- dict with values
        (like: "0.3133: [0.12, 0.13, ..., 3.1]")

        - ``progress`` -- ProgressNotebook instance.

        Return:

        - ``results_param_arrays`` -- dict
        (like: results_param_arrays[param][var][time]
                = [0.12, 0.13, ..., 3.1])
        '''

        results_param_arrays = {}

        def gen(result):
            for key in result:
                step_0_0 = result[key].replace('...,', "")
                step_0_1 = re.subn(r'\[\s+', "[", step_0_0)[0]
                step_0 = re.subn(r'\.\s+', ".0,", step_0_1)[0]
                step_1 = re.subn(r'\s+', ",", step_0)[0]
                step_2 = step_1.replace('.]', '.0]')
                step_3 = step_2.replace('[,', '[')
                step_4 = step_3.replace("nan", "None")
                yield((key, eval(step_4)))

        steps = 0
        for param in results_params:
            for var, data in enumerate(results_params[param]):

                if param not in results_param_arrays:
                    results_param_arrays[param] = {}

                try:
                    lines = data.split('\n')
                    result = {}

                    for line in lines:
                        if ':' in line:
                            key, val = line.split(':')
                            result[key] = val[1:]
                        else:
                            val = line
                            result[key] += val

                    result_t = [(float(key), val) for key, val in gen(result)]

                except:
                    results_param_arrays[param][var] = None
                    continue

                results_param_arrays[param][var] = dict(result_t)
                steps += 1
                progress.succ(steps)
                # print(steps)
        times = [key[0] for key in result_t]
        # result_x = np.array([result_t[key] for key in result_t]).T
        return(times, results_param_arrays)

    def remove_out(self):
        
        '''Clear ``.out`` and ``.mp4`` files from out folder.'''

        out_dir = os.path.join(self.hd_dir, 'problems',
                               self.model_path, "out")
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

    def extract_out(self, params_idx, data):

        '''extract data from ``.out`` files to
        ``data[params_idx]``'''

        out_dir = os.path.join(self.hd_dir, 'problems',
                               self.model_path, "out")
        listdir = os.listdir(out_dir)

        replacer_id = self.replacer_id
        
        outs = [os.path.join(out_dir, file_name)
                for file_name in listdir
                if ('.out' in file_name) and (replacer_id not in file_name)]
        # print(outs)

        data[params_idx] = []
        for out in outs:
            param_data = "failure"
            with open(out) as f:
                param_data = f.read()
            data[params_idx].append(param_data)
        # return(data)

    def rename_out(self, params_idx):

        '''rename ``.out`` and ``.mp4`` files in order to
        prevent their revriting.
        (see also ``self.replacer_id`` in ``self.__init__``)'''

        out_dir = os.path.join(self.hd_dir, 'problems',
                               self.model_path, "out")
        listdir = os.listdir(out_dir)

        replacer_id = self.replacer_id
        replacer = replacer_id+str(params_idx)

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
