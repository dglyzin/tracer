from gens.hs.gen_env.cpp.env.base.base_common import GenBaseCommon
from spaces.some_space.someClasses import Params


class GenCommon(GenBaseCommon):
    
    def __init__(self, net):
        self.net = net
        self.net.params = Params()

    def set_params_for_array(self, funcNamesStack):
        '''
        DESCRIPTION::

        factorize ``funcNames`` into blockNumber's classes
        i.e. ``namesAndNumbers[blockNumber] = [names for blockNumber]``

        Input:

        :param funcNamesStack: from all cpp func generators
        (centrals, bounds, interconnects)
        '''

        # factorize funcNames into blockNumber's classes
        # i.e. namesAndNumbers[blockNumber] = [names for blockNumber]
        namesAndNumbers = {}
        for funcName in funcNamesStack:
            blockNumber = int(self.get_number(funcName))
            if blockNumber in namesAndNumbers.keys():
                namesAndNumbers[blockNumber].append(funcName)
            else:
                namesAndNumbers[blockNumber] = [funcName]

        self.net.params.namesAndNumbers = namesAndNumbers

    def get_number(self, funcName):
        '''
        DESCRIPTION::

        From ``funcName`` get ``blockNumber``

        EXAMPLE::

        ``'Block0CentralFunction1' -> '0'``
        '''
        # cut name Block from funcName
        tail = funcName[5:]
        blockNumber = []
        # find end of number
        for num in tail:
            if num in '0123456789':
                blockNumber.append(num)
            else:
                break
        return(blockNumber[0])
