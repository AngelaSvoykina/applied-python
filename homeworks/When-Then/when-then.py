# coding=utf-8

def whenthen(func):
    def wrapper(*args, **kwargs):
        if len(wrapper.__when) != len(wrapper.__then):
            raise ValueError('Condition when does not have then statement!')

        for i, condition in enumerate(wrapper.__when):
            if condition(*args, **kwargs):
                return wrapper.__then[i](*args, **kwargs)
        return func(*args, **kwargs)

    wrapper.__when = []
    wrapper.__then = []

    def when(new_func):
        if len(wrapper.__when) - len(wrapper.__then) != 0:
            raise ValueError('Condition when does not have then statement!')
        wrapper.__when.append(new_func)
        return wrapper

    def then(new_func):
        if len(wrapper.__when) - len(wrapper.__then) != 1:
            raise ValueError('Condition then does not have when statement!')
        wrapper.__then.append(new_func)
        return wrapper

    wrapper.then = then
    wrapper.when = when

    return wrapper


@whenthen
def fract(x):
    return x * fract(x - 1)


@fract.when
def fract(x):
    return x == 0


@fract.then
def fract(x):
    return 1


@fract.when
def fract(x):
    return x > 5


@fract.then
def fract(x):
    return x * (x - 1) * (x - 2) * (x - 3) * (x - 4) * fract(x - 5)


print(fract(0))
print(fract(2))
print(fract(6))
