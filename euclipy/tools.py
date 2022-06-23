from sympy import pi

def euclicache(func) -> callable:
    '''Creates a cache to hold the results of calls to __new__ of the geometric classes.'''
    cache = {}
    def wrapper(cls, label = None, *args) -> object:
        '''Checks if args are in cache. If so, returns the cached instance. If not, calls __new__ and adds the result to the cache.'''
        if label:
            args = (cls, cls.canonical_label(label)) + args
        else:
            args = (cls,)

        if args in cache:
            return cache[args]

        cache[args] = func(*args)
        return cache[args]
        
    return wrapper

def pairs_in_iterable(iterable) -> list:
    '''Returns a list of all pairs of two found in an interable.'''
    return [(a, b) for index, a in enumerate(iterable) for b in iterable[index + 1:]]

def deg_to_rad(deg):
    return deg * pi / 180
