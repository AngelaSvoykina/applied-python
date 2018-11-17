from time import time
import collections.abc
import inspect


def profile(foo, class_name=None):
    def wrapper(*args, **kwargs):
        t_before = time()
        prefix = f'{class_name}.' if class_name else ''
        print('`{}{}` started '.format(prefix, foo.__name__))
        res = foo(*args, **kwargs)
        t_after = time()
        d_t = t_after - t_before
        print('`{}{}` finished in {} '.format(prefix, foo.__name__, str(d_t)))
        return res

    if inspect.isclass(foo):
        for attr in foo.__dict__:
            if isinstance(getattr(foo, attr), collections.Callable):
                setattr(foo, attr, profile(getattr(foo, attr), foo.__name__))
        return foo
    else:
        return wrapper


@profile
class Bar:
    def __init__(self, a=1):
        self.a = 1
        pass

    def bar(self):
        pass


@profile
def func():
    pass


if __name__ == '__main__':
    func()
    s = Bar()
    s.bar()
