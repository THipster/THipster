def logger(name: str):
    def wrapper(function):
        def internal_wrapper(*args, **kwargs):
            print(f'{name} starting')
            res = function(*args, **kwargs)
            print(f'{name} returned :\n{str(res)}')
            return res
        return internal_wrapper
    return wrapper