import functools

def cached(func):
    """
    A simple decorator to cache the result of a property or method.
    In a real implementation, this might need to be aware of the current candle timestamp
    to invalidate the cache when time moves forward.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Create a cache storage on the instance if it doesn't exist
        if not hasattr(self, '_cache'):
            self._cache = {}
        
        # Create a key based on the function name and arguments
        key = (func.__name__, args, tuple(kwargs.items()))
        
        # Check if we have a cached value
        if key in self._cache:
            return self._cache[key]
        
        # Calculate and store
        result = func(self, *args, **kwargs)
        self._cache[key] = result
        return result
        
    return wrapper
