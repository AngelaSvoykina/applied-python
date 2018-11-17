from time import time
import inspect


def profile(foo):
    def profile_decorator(*args, **kwargs):
        t_before = time()
        print('`{}` started '.format(foo.__name__))
        res = foo(*args, **kwargs)
        t_after = time()
        d_t = t_after - t_before
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
            if type(x) == type(self.__init__):  # it is an instance method
                return profile(x)  # this is equivalent of just decorating the method with profile
            else:
                return x

    if inspect.isclass(foo):
        return NewCls
    else:
        return profile_decorator


@profile
class Bar:
    def __init__(self, a=1):
        self.a = 1
        pass


@profile
def foo():
    pass


if __name__ == '__main__':
    foo()
    s = Bar()
