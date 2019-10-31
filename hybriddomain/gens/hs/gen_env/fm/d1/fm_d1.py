class GenFmD1():

    '''Extract ``functionMaps`` for vertexs
    of bounds or ic intervals. For 1d.'''
    
    def gen_fm_for_vertexs(self, params_vertexs, functionMaps,
                           namesAndNumbers):
        for fm_param in params_vertexs:
            sideName = "side"+str(fm_param.side_num)
            funcName = fm_param.funcName
            blockNumber = fm_param.blockNumber

            idx = namesAndNumbers[blockNumber].index(funcName)
            # logger.debug("funcName=%s " % str(fm_param.funcName))
            # logger.debug("sideName, idx= %s, %s " % (str(sideName), str(idx)))
            
            value_to_update = idx

            # update functionMaps:
            # if sideName not in functionMaps[blockNumber].keys():
            functionMaps[blockNumber].update({sideName:
                                              value_to_update})
