from time import time
import collections
import inspect
import types


def profile(foo, class_name=None):
    def wrapper(*args, **kwargs):
        t_before = time()
        if class_name:
            print('`{}.{}` started '.format(class_name, foo.__name__))
        else:
            print('`{}` started '.format(foo.__name__))
        res = foo(*args, **kwargs)
        t_after = time()
        d_t = t_after - t_before

        if class_name:
            print('`{}.{}` finished in {}'.format(class_name, foo.__name__, str(d_t)))
        else:
            print('`{}` finished in {}'.format(foo.__name__, str(d_t)))
        return res

    class NewCls(object):
        def __init__(self, *args, **kwargs):
            t_before = time()
            print('`{}.__init__ started` '.format(foo.__name__))
            self.oInstance = foo(*args, **kwargs)
            t_after = time()
            d_t = t_after - t_before
            print('`{}.__init__ finished in {}`'.format(foo.__name__, str(d_t)))

        def __getattribute__(self, s):
            try:
                x = super(NewCls, self).__getattribute__(s)
            except AttributeError:
                pass
            else:
                return x
            x = self.oInstance.__getattribute__(s)
            if isinstance(x, collections.Callable):
                return profile(x, foo.__name__)
            else:
                return x

    if inspect.isclass(foo):
        return NewCls
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
