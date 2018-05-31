from jinja2 import Environment, FileSystemLoader


class GenBase():
    
    def __init__(self):
        pathToTemplates = 'gens/hs/cpp/templates'
        self.env = Environment(loader=FileSystemLoader(pathToTemplates))
        # self.env.filters['len'] = len
        # self.env.filters['enumerate'] = enumerate

    def fill_func_names_stack(self, funcNamesStack):
        
        # check if funcNamesStack alredy exist:
        if 'funcNamesStack' in self.__dict__:
            '''
            for funcName in funcNamesStack:
                if funcName not in self.funcNamesStack:
                    self.funcNamesStack.append(funcName)
            '''
            self.funcNamesStack.extend(funcNamesStack)

            # remove duplicates:
            self.funcNamesStack = list(set(self.funcNamesStack))
        else:
            self.funcNamesStack = funcNamesStack


class Params:
    '''
    DESCRIPTION:
    Represent part of block with
    different equation (from default).
    
    '''
    pass
    
