class Object(object):
    '''
    DESCRIPTION:
    For common methods.
    For Interconnect, Equation, Bound, Block. 
    '''
    ## PRINT
    def __repr__(self):
        '''
        DESCRIPTION:
        For print(model).
        '''
        out = ""
        outDict = self.getPropertiesDict()
        # lists = ('Blocks', 'Interconnects', 'Equations', 'Bounds')
        for key in outDict:
            outVal = ""
            if type(outDict[key]) == list:
                for i in range(len(outDict[key])):
                    outVal = (outVal
                              + "\n\n"
                              + str(key)[:-1] + " " + str(i)
                              + "\n"
                              + str(outDict[key][i]))
            else:
                outVal = str(outDict[key])

            out = (out
                   + str(key)
                   + '\n ############## \n'
                   + outVal
                   + '\n\n')
        return(out)
    
