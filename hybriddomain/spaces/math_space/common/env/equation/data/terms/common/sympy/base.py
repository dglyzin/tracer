class CommonSympy():

    def add_args(self, var, pattern):
        
        '''Add x, y to var. pattern is reg_pattern
        to extract data from.'''

        free_vars = self.get_free_vars(pattern)
        
        # add args (",x" or ",x,y" or "x,y,z"):
        args = ''
        for free_var in free_vars:
            args += ', %s' % (free_var)
        args += ')'
        
        # FOR add args to var:
        '''
        if self.params['dim'] == 1:
            x = ', x)'
        elif self.params['dim'] == 2:
            x = ', x, y)'
        '''

        # U(t-1)
        if '(' in var:
            var = var[:-1] + args
        else:
            var = var + '(' + 't'+args
        # END FOR
        
        return(var)

    def get_free_vars(self, pattern):
        free_vars = {}

        # find diff orders (free_var: x, order: 1):
        for free_var in 'xyz':
            try:
                order = pattern.group('val_'+free_var)
                if order is not None:
                    free_vars[free_var] = order
            except IndexError:
                continue
        return(free_vars)
