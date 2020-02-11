from hybriddomain.solvers.hs.remoterun.io_routine import IORoutine


class MSIORoutine(IORoutine):
    
    def copy_model_files(self, paths):
        
        logger = self.logger

        # 1 copy model files to sn:
        de_model_path = paths[self.den]['project_path']
        # sn_model_path = paths[self.sn]['project_path_absolute']
        sn_out_folder = paths[self.sn]['out_folder']

        logger.debug("de_model_path:")
        logger.debug(de_model_path)
        logger.debug("sn_model_path:")
        logger.debug(sn_out_folder)
        self.copy_files(de_model_path, sn_out_folder, "models")

    def add_paths_to_model(self, paths, model):
        pass
