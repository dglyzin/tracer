from copy import deepcopy as copy
from copy import copy as weak_copy


class Dbg():
    def __init__(self, dbg, dbgInx):
        self.dbg = dbg
        self.dbgInx = dbgInx

    def print_dbg(self, *args):
        if self.dbg:
            for arg in args:
                print(self.dbgInx*' '+str(arg))
            print('')


class Property(object):
    '''
    DESCRIPTION:

    Descriptor for Interval.
    '''
    def __init__(self, attrName):
        self.attrName = attrName
    
    def __get__(self, instance, owner=None):
        '''
        DESCRIPTION:

        Instance is instance of UseProperty class.
        getattr get atrName of instance UseProperty class.
        '''
        # print("get")
        # print(instance)
        return(getattr(instance, self.attrName))
    
    def __set__(self, instance, value):
        '''
        DESCRIPTION:

        If value is dict it update instance.attrName dict
           if self.attrName is not dict, it replace it
              by dict value
        else
           it just set instance.attrName by value. 
        '''
        # print("set")
        if type(value) is not dict:
            return(setattr(instance, self.attrName, value))

        old_data = getattr(instance, self.attrName)
        
        # print("old_data")
        # print(old_data)
        
        if type(old_data) == dict:
            new_data = copy(old_data)
            new_data.update(value)
        else:
            new_data = value

        # print("new_data")
        # print(new_data)
        
        return(setattr(instance, self.attrName, new_data))


class Interval(list):

    ''' Interval is open interval. So all it's
    method (including ``split``) sugested. Except
    ``contains_as_closed``.

    Warning:
    
    Do not forget about bug with self.split_all.
    Use it like ``k.split_all([i, j], [])``
    instead of ``k.split_all([i, j])``
    '''

    # descriptor at self._name
    name = Property("_name")

    def __init__(self, _list, name=0):
        # for debug
        self.debug = Dbg(False, 3)

        list.__init__(self, _list)
                
        self._name = name

    def __contains__(self, x):
        
        '''Main. When self used as open intervals.'''

        if self[0] < x < self[1]:
            return(True)
        else:
            return(False)

    def contains_as_closed(self, x):

        if type(x) is list:
            if (self[0] <= x[0] <= self[1] and
                self[0] <= x[1] <= self[1]):
                return(True)
        else:
            if self[0] <= x <= self[1]:
                return(True)
            else:
                return(False)
                
    def split_all(self, intervals_list, result):
        '''
        DESCRIPTION:

        Split self at regions with names interval.name
        where interval in intervals_list.

        Warning:

        Due to some python bug second argument
        cannot be used with default ``[]`` value.
        Because of that one need to write
        ``k.split_all([i, j], [])`` instead of
        ``k.split_all([i, j])``. (It Seems he remembering
        data from previus usage of class Interval
        (in ``self`` parameter of result (``res.split(first)``)))

        Example:

        >>> i, j, k = pms.Interval([1, 2], name='i'),\
        pms.Interval([2, 3], name='j'),\
        pms.Interval([1.5, 2.5], name='k')
        
        >>> t = k.split_all([i, j], [])

        >>> t[0], t[0].name
        ([1.5, 2], 'i')

        >>> t[1], t[1].name
        ([2, 2.5], 'j')

        '''
        self.debug.print_dbg("FROM Interval.split_all")

        self.debug.print_dbg("self")
        self.debug.print_dbg(self)
        
        if len(result) == 0:
            result.append(self)

        if len(intervals_list) == 0:
            self.debug.print_dbg("result")
            self.debug.print_dbg(result)
            return(result)
        
        first, rest = intervals_list[0], intervals_list[1:]

        new_res = []
        for res in result:
            self.debug.print_dbg("res for 'self' check:")
            self.debug.print_dbg("(problem here):")
            self.debug.print_dbg(res)
       
            new_res.extend(res.split(first))
                
        return(self.split_all(rest, new_res))

    def split(self, interval):
        '''
        DESCRIPTION:

        Split self at regions with names from
        original and interval.name.
        
        RETURN:

        Never empty.

        Example:

        >>> a = Interval([1, 3], name='a')
        >>> b = Interval([1, 2], name='b')
        
        >>> cs = a.split(b)
        >>> cs[0], cs[0].name
        ([1, 2], 'a')

        >>> cs[1], cs[1].name
        ([2, 3], 'b')
        '''
        interval_from = self

        self.debug.print_dbg("interval_from (equal self)")
        self.debug.print_dbg(interval_from)

        self.debug.print_dbg("self from split (problem here):")
        self.debug.print_dbg(self)

        self.debug.print_dbg("interval")
        self.debug.print_dbg(interval)

        if (interval[0] not in interval_from and
            interval[1] not in interval_from):
            # if interval not in interval_from

            # if interval_from not in interval
            if (interval[1] <= interval_from[0] or
                interval[0] >= interval_from[1]):
                # do nothing
                return([interval_from])
            else:
                # if interval_from in interval
                
                # rename interval_from
                # if name is dict update it twice
                # else just set interval.name
                # (see Property.__set__)
                interval_from.name = interval_from.name
                interval_from.name = interval.name
                return([interval_from])

        elif(interval[0] in interval_from):
            # if interval intersects interval_from by left side

            result = []
            iLeft = Interval([interval_from[0], interval[0]])
            iLeft.name = interval_from.name
            result.append(iLeft)

            if(interval[1] in interval_from):
                # if interval in interval_from

                iRight = Interval([interval[1], interval_from[1]])
                iRight.name = interval_from.name

                iMidle = Interval([interval[0], interval[1]])

                # if name is dict update it twice
                # else just set interval.name
                # (see Property.__set__)
                iMidle.name = interval_from.name
                iMidle.name = interval.name

                result.append(iMidle)
                result.append(iRight)
            else:
                # if right side of interval not in interval_from
                iRight = Interval([interval[0], interval_from[1]])

                # if name is dict update it twice
                # else just set interval.name
                # (see Property.__set__)
                iRight.name = interval_from.name
                iRight.name = interval.name

                result.append(iRight)
            return(result)

        elif(interval[1] in interval_from):
            # if interval intersects interval_from by right side

            iLeft = Interval([interval_from[0], interval[1]])

            # if name is dict update it twice
            # else just set interval.name
            # (see Property.__set__)
            iLeft.name = interval_from.name
            iLeft.name = interval.name

            iRight = Interval([interval[1], interval_from[1]])
            iRight.name = interval_from.name
            return([iLeft, iRight])


class TestCase():

    def __init__(self):
        # for debug
        self.debug = Dbg(True, 1)

        self.tests_cases_for_interval = [
            "[0, 10];[0, 3];[5, 7]",  # common
            "[0, 10];[0, 3];[5, 13]",  # right too far
            "[2.5, 10];[0, 3];[5, 7]",  # left too far
            "[0, 10];[0, 3];[3, 7]",  # common point
            "[1, 10];[0, 1];[5, 7]"  # left intersects in point
        ]
        
        self.tests_results_for_interval = [
            # case 0: "[0, 10];[0, 3];[5, 7]"
            [Interval([0, 3], name=1),
             Interval([3, 5], name=0),
             Interval([5, 7], name=2),
             Interval([7, 10], name=0)],

            # case 1: "[0, 10];[0, 3];[5, 13]"
            [Interval([0, 3], name=1),
             Interval([3, 5], name=0),
             Interval([5, 10], name=2)],

            # case 2: "[2.5, 10];[0, 3];[5, 7]"
            [Interval([2.5, 3], name=1),
             Interval([3, 5], name=0),
             Interval([5, 7], name=2),
             Interval([7, 10], name=0)],

            # case 3: "[0, 10];[0, 3];[3, 7]"
            [Interval([0, 3], name=1),
             Interval([3, 7], name=2),
             Interval([7, 10], name=0)],
            
            # case 4: "[1, 10];[0, 1];[5, 7]"
            [Interval([1, 5], name=0),
             Interval([5, 7], name=2),
             Interval([7, 10], name=0)]
        ]

        self.tests_results_for_interval_dict = [
            # case 0: "[0, 10];[0, 3];[5, 7]"
            [Interval([0, 3], name={'num': 1}),
             Interval([3, 5], name={'num': 0}),
             Interval([5, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})],

            # case 1: "[0, 10];[0, 3];[5, 13]"
            [Interval([0, 3], name={'num': 1}),
             Interval([3, 5], name={'num': 0}),
             Interval([5, 10], name={'num': 2})],

            # case 2: "[2.5, 10];[0, 3];[5, 7]"
            [Interval([2.5, 3], name={'num': 1}),
             Interval([3, 5], name={'num': 0}),
             Interval([5, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})],

            # case 3: "[0, 10];[0, 3];[3, 7]"
            [Interval([0, 3], name={'num': 1}),
             Interval([3, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})],
            
            # case 4: "[1, 10];[0, 1];[5, 7]"
            [Interval([1, 5], name={'num': 0}),
             Interval([5, 7], name={'num': 2}),
             Interval([7, 10], name={'num': 0})]
        ]

    def tests_intervals_dict(self):

        tests_cases = self.tests_cases_for_interval
        tests_results = self.tests_results_for_interval_dict

        for input_string in tests_cases:
            res = self.interval_interface_dict(input_string)

            # check test
            assert(res == tests_results[tests_cases.index(input_string)])

            # print result
            self.debug.print_dbg("for ", input_string)
            self.debug.print_dbg('res = ')
            for r in res:
                self.debug.print_dbg("name %s val %s " % (str(r.name), str(r)))
        return(True)

    def interval_interface_dict(self, input_string="[0, 10];[0, 3];[5, 7]"):
        ivs = [Interval(eval(sInterval), name={'num': num})
               for num, sInterval in enumerate(input_string.split(';'))]
        return(ivs[0].split_all(ivs[1:], []))

    def tests_intervals(self):

        tests_cases = self.tests_cases_for_interval
        tests_results = self.tests_results_for_interval

        for input_string in tests_cases:
            res = self.interval_interface(input_string)

            # check test
            assert(res == tests_results[tests_cases.index(input_string)])

            # print result
            self.debug.print_dbg("for ", input_string)
            self.debug.print_dbg('res = ')
            for r in res:
                self.debug.print_dbg("name %s val %s " % (str(r.name), str(r)))
            return(True)

    def interval_interface(self, input_string="[0, 10];[0, 3];[5, 7]"):
        ivs = [Interval(eval(sInterval), name=num)
               for num, sInterval in enumerate(input_string.split(';'))]
        return(ivs[0].split_all(ivs[1:], []))
