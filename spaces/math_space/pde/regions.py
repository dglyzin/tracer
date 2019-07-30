# -*- coding: utf-8 -*-
'''
Created on Mar 19, 2015

@author: dglyzin
'''
from collections import OrderedDict
from pandas import DataFrame


class Region(object):
    def __init__(self, **bdict):
        '''
        '''
        self.dim = bdict['dim']
    '''
    def _set_from_coords(self, coords):
        if self.dim > 1:
            self.xfrom = coords[0][0]
            self.xto = coords[1][0]
            self.yfrom = coords[0][1]
            self.yto = coords[1][1]
        if self.dim > 2:
            self.zfrom = coords[0][2]
            self.zto = coords[1][2]
    '''
    def __repr__(self):
        
        col = ['from', 'to'] 
        out = [[self.xfrom, self.xto]]
        row = ['x']

        if self.dim == 2:
            out.append([self.yfrom, self.yto])
            row.append('y')
        if self.dim == 3:
            out.append([self.zfrom, self.zto])
            row.append('z')
            
        d = DataFrame(out, index=row, columns=col)
        return(str(d))

    def __eq__(self, o):
        cond = (self.dim == o.dim
                and self.xfrom == o.xfrom
                and self.xto == o.xto)
    
        if self.dim == 2:
            cond = (cond and self.yfrom == o.yfrom
                    and self.yto == o.yto)

        if self.dim == 3:
            cond = (cond and self.zfrom == o.zfrom
                    and self.zto == o.zto)

        return(cond)

    def _set_coords_from_bdict(self, bdict):
        
        self.xfrom = bdict["xfrom"]
        self.xto = bdict["xto"]

        if self.dim > 1:
            self.yfrom = bdict["yfrom"]
            self.yto = bdict["yto"]

        if self.dim > 2:
            self.zfrom = bdict["zfrom"]
            self.zto = bdict["zto"]

    def _update_prop(self, propDict, dim):
        if dim > 1:
            propDict.update({"xfrom": self.xfrom})
            propDict.update({"xto": self.xto})
            propDict.update({"yfrom": self.yfrom})
            propDict.update({"yto": self.yto})
        if dim > 2:
            propDict.update({"zfrom": self.zfrom})
            propDict.update({"zto": self.zto})


class BoundRegion(Region):
    '''
    Inputs:

    side - side in block;
    dim, boundNumber;
    *from, *to - regions, where * means x y or z,
                 according of dimension.

    Examples:

    >>> e = BoundRegion(side=0, dim=1, boundNumber=0,
                        xfrom=0, xto=1)

    >>> bdict = {'side': 0, 'dim': 1, 'boundNumber': 0,
                'xfrom': 0, 'xto': 1}
    >>> e = BoundRegion(**bdict)
    '''
    def __init__(self, **bdict):
        
        Region.__init__(self, **bdict)

        self.fillProperties(bdict)

    def __repr__(self):
        out = ""
        if self.dim != 1:
            out += Region.__repr__(self)
        out += "\nside_num: %s \n" % (str(self.side_num))
        out += "boundNumber: %s\n" % (str(self.boundNumber))
        return(out)

    def __eq__(self, o):
        cond = Region.__eq__(self, o)
        cond = (cond and self.side_num == o.side_num
                and self.boundNumber == o.boundNumber)
        return(cond)

    def fillProperties(self, bdict):
        
        ''''''

        self.boundNumber = bdict["BoundNumber"]

        self.side_num = bdict["Side"]
        
        if self.dim != 1:
            try:
                self._set_coords_from_bdict(bdict)
            except KeyError:
                pass

    def getPropertiesDict(self, dim):
        propDict = OrderedDict([
            ("BoundNumber", self.boundNumber),
            ("Side", self.side_num)])
        self._update_prop(propDict, dim)
        return propDict


class InitialRegion(Region):
    '''
    Inputs:

    dim, initialNumber;
    *from, *to - regions, where * means x y or z,
                 according of dimension.

    Examples:

    >>> e = InitialRegion(dim=1, initialNumber=0,
                          xfrom=0, xto=1)

    >>> bdict = {'dim': 1, 'initialNumber': 0,
                 'xfrom': 0, 'xto': 1}
    >>> e = InitialRegion(**bdict)
    '''

    def __init__(self, **bdict):

        Region.__init__(self, **bdict)

        self.fillProperties(bdict)

    def __repr__(self):
        out = Region.__repr__(self)
        out += "\ninitialNumber: %s\n" % (str(self.initialNumber))
        return(out)

    def __eq__(self, o):
        cond = Region.__eq__(self, o)
        cond = (cond and self.initialNumber == o.initialNumber)
        return(cond)

    def fillProperties(self, bdict):
        self.initialNumber = bdict["InitialNumber"]
        self._set_coords_from_bdict(bdict)
        
    def getPropertiesDict(self, dim):
        propDict = OrderedDict([
            ("InitialNumber", self.initialNumber),
            ("xfrom", self.xfrom),
            ("xto", self.xto)])
        self._update_prop(propDict, dim)
        return propDict


class EquationRegion(Region):
    '''
    Inputs:

    dim, EquationNumber;
    *from, *to - regions, where * means x y or z,
                 according of dimension.

    Examples:

    >>> e = EquationRegion(dim=1, equationNumber=0,
                            xfrom=0, xto=1)

    >>> bdict = {'dim': 1, 'equationNumber': 0,
                 'xfrom': 0, 'xto': 1}
    >>> e = EquationRegion(**bdict)
    '''

    def __init__(self, **bdict):

        Region.__init__(self, **bdict)

        self.fillProperties(bdict)

    def __repr__(self):
        out = Region.__repr__(self)
        out += "\nequationNumber: %s\n" % (str(self.equationNumber))
        return(out)

    def __eq__(self, o):
        cond = Region.__eq__(self, o)
        cond = (cond and self.equationNumber == o.equationNumber)
        return(cond)

    def fillProperties(self, bdict):
        self.equationNumber = bdict["EquationNumber"]
        self._set_coords_from_bdict(bdict)

    def getPropertiesDict(self, dim):
        propDict = OrderedDict([
            ("EquationNumber", self.equationNumber),
            ("xfrom", self.xfrom),
            ("xto", self.xto)])
        self._update_prop(propDict, dim)
        return propDict
