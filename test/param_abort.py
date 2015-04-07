from functools import wraps


def param_abort(f):
    '''This decorator avoids the execution of multiple nose parameterized
    tests, once the first one has failed. Just add the decorator AFTER the
    parameterized expression decorator'''
    @wraps(f)
    def test_wrapper(*args, **kwargs):
        kls = args[0].__class__
        if not hasattr(kls, '__failed_flag'):
            kls.__failed_flag = False
        if kls.__failed_flag:
            raise Exception('Parameterized test skipped, previous errors')
        kls.__failed_flag = True
        f(*args, **kwargs)
        kls.__failed_flag = False
    return test_wrapper
