import inspect
from itertools import tee, filterfalse

def raise_if(boolean, message):
    if boolean:
        raise ValueError(message)

def raise_if_not(boolean, message):
    '''Similar to assert, but won't be optimised out in production build'''
    raise_if(not boolean, message)

def find(predicate, array):
    '''Find the first instance in array that matches the predicate'''
    return next(filter(predicate, array), None)

def partition(iterable, predicate):
    '''Return two iterables, the elements of iterable for which the predicate is true, 
    and the elements for which the predicate is false.'''
    iter1, iter2 = tee(iterable)
    return filter(predicate, iter1), filterfalse(predicate, iter2)

def lpartition(iterable, predicate):
    '''Strictly-evaluated version of partition'''
    trues, falses = partition(iterable, predicate)
    return list(trues), list(falses)

class SingletonMixin:
    value = None
    def __new__(cls):
        if not cls.value:
            cls.value = super().__new__(cls)
        return cls.value

class ValueEqualityMixin:
    '''Value equality instead of reference equality'''
    def __eq__(self, other):
        return type(self) == type(other) and self.__dict__ == other.__dict__

def constructor_str(obj):
    if type(obj) == str:
        return "'{0}'".format(obj)
    elif type(obj) in (bool, int, float, complex, type(None)):
        return str(obj)
    elif type(obj) in (list, tuple):
        contents = ', '.join(constructor_str(e) for e in obj)
        return '[{0}]'.format(contents) if type(obj) == list else '({0})'.format(contents)
    else:
        cls = obj.__class__
        if list(inspect.signature(cls.__new__).parameters) == ['args', 'kwargs']:
            args = inspect.signature(cls.__init__).parameters
        else:
            args = inspect.signature(cls.__new__).parameters

        arg_strs = [str(a) for a in args.values()]
        raise_if(any('*' in s for s in arg_strs), "constructor_str doesn't work for args or kwargs " +
            "as there's no way to reconstruct the values automatically. Error encountered on value: {0}".format(obj))

        arg_strs_no_def_vals = [s.split('=')[0] for s in arg_strs]
        arg_values = [constructor_str(obj.__dict__[a]) for a in arg_strs_no_def_vals[1:]]
        return '{0}({1})'.format(cls.__name__, ', '.join(arg_values))

class DefaultDict(dict):
    '''
    Like collections.defaultdict except this doesn't mutate the dict by adding key=default_factory() on __getitem__(key).
    This fixes this gotcha:
        d = DefaultDict()
        print(d['a']) # prints None, as expected
        print(d.keys()) # prints dict_keys(['a']), even though we never added it to the dict 'd'
    but introduces the following gotcha:
        d = DefaultDict(list)
        d['a'].append('5')
        print(d['a']) # prints [], as we never added the key 'a' to the dict 'd', so we have no reference to the list we mutated 
    '''
    def __init__(self, default_factory=lambda: None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)
        return self.default_factory()