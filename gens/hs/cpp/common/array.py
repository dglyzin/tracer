from gens.hs.cpp.common.base import GenBase


class Gen(GenBase):
    '''
    Fill self.namesAndNumbers for array template:
    (see self.set_params_for_array)

    Generate cpp:
    (see get_out_for_array)
    '''

    def get_out_for_array(self):
        '''
        DESCRIPTION:
        params.set_params_for_array must be called first.
        '''
        template = self.env.get_template('array.template')

        args = {
            'namesAndNumbers': self.namesAndNumbers,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def set_params_for_array(self, funcNamesStack):
        '''
        DESCRIPTION:
        factorize funcNames into blockNumber's classes
        i.e. namesAndNumbers[blockNumber] = [names for blockNumber]

        Input:
        funcNamesStack from all cpp func generators
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

        self.namesAndNumbers = namesAndNumbers

    def get_number(self, funcName):
        '''
        DESCRIPTION:
        From funcName get blockNumber

        EXAMPLE:
        'Block0CentralFunction1' -> '0'
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
