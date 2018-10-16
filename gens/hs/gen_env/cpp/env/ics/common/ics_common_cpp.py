class GenCppCommon():
    
    def parse_equations(self, eSystem, dim, blockNumber,
                        side_num, firstIndex, secondIndex):

        # for equatioin cpp:
        self.set_eq_base_params(eSystem,
                                dim, blockNumber)
        self.set_eq_spec_params(eSystem, side_num,
                                firstIndex, secondIndex)
        parsedValues = self.get_eq_cpp(eSystem)
        return(parsedValues)

    def set_eq_spec_params(self, eSystem, side_num,
                           firstIndex, secondIndex):
        eSystem.cpp.set_diff_type_ic(side_num=side_num,
                                     firstIndex=firstIndex,
                                     secondIndex=secondIndex)
    
