from envs.hs.model.model_base import ModelBase


class ModelGenCpp(ModelBase):
    pass


'''
    def getMaxDerivOrder(self):
        d = DerivativeHandler()
        return(d.orderOfSystem(self.equations[0].system,
                               self.params, self.equations[0].vars))
    
    
    def determineDelay(self):
        d = DelayHandler()
        return d.determineDelay(self.equations[0].system,self.params, self.equations[0].vars)

    def createCPPandGetFunctionMaps(self, cppFileName, preprocessorFolder, nocppgen):
        #generator1
        # try:
        gridStep = [self.gridStepX, self.gridStepY, self.gridStepZ]
        reviewer = Reviewer(self.equations, self.blocks, self.initials,
                            self.bounds, gridStep, self.params,
                            self.paramValues, self.defaultParamsIndex)
        reviewer.ReviewInput()
        haloSize = self.getHaloSize()
        mDO = self.getMaxDerivOrder()
        delay_lst = []  # self.determineDelay()
        
        gen = FuncGenerator(delay_lst, mDO, haloSize, self.equations,
                            self.blocks, self.initials, self.bounds,
                            self.interconnects, gridStep, self.params,
                            self.paramValues, self.defaultParamsIndex,
                            preprocessorFolder)
        outputStr, functionMaps = gen.generateAllFunctions()
        # except Exception as ex:
        #    print("###")
        #    print(ex)
        # else:
        if not nocppgen:
            f = open(cppFileName,'w')
            f.write(outputStr)
            f.close()
        return (functionMaps, gen.delays)
        #generator2
        #generateCfromDict(self.toDict(),cppFileName)
'''
