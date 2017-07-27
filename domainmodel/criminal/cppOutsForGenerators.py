from jinja2 import Environment, FileSystemLoader


class CppOutsForGenerators():
    '''
    DESCRIPTION:

    '''
    def __init__(self):
        # self.params = params
        pathToTemplates = 'domainmodel/criminal/templates'
        self.env = Environment(loader=FileSystemLoader(pathToTemplates))
        # self.env.filters['len'] = len
        # self.env.filters['enumerate'] = enumerate
    
    def get_out_for_definitions(self, params):
        template = self.env.get_template('definitions.template')

        args = {
            'gridArgs': params.gridArgs,
            'blocksArgs': params.blocksArgs,
            'paramsLen': params.paramsLen,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_array(self, params):
        template = self.env.get_template('array.template')

        # FOR get blockNumber's from funcNames
        def get_number(funcName):
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

        # factorize funcNames into blockNumber's classes
        # i.e. namesAndNumbers[blockNumber] = [names for blockNumber]
        namesAndNumbers = {}
        for funcName in params.funcNamesStack:
            blockNumber = get_number(funcName)
            if blockNumber in namesAndNumbers.keys():
                namesAndNumbers[blockNumber].append(funcName)
            else:
                namesAndNumbers[blockNumber] = [funcName]
        # END FOR
                
        args = {
            'namesAndNumbers': namesAndNumbers,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_centrals(self, params):
        template = self.env.get_template('central_functions.template')

        args = {
            'equations': params.equations,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_interconnects(self, params):
        template = self.env.get_template('interconnects.template')

        args = {
            'ics': params.ics,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_bounds(self, params):
        template = self.env.get_template('bound_conditions.template')

        args = {
            'bounds': params.bounds,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_parameters(self, params):
        template = self.env.get_template('params.template')

        args = {
            'params': params.parameters,
            'paramValues': params.parametersVal,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)

    def get_out_for_initials(self, params):
        template = self.env.get_template('initial_conditions.template')

        args = {
            'blocks': params.blocks,
            'enumerate': enumerate,
            'len': len
        }

        # args like in dict()
        out = template.render(args)
        return(out)
