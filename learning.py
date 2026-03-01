from contextlib import contextmanager


def decorator(function):
    def inner(*args, **kwargs):
        print("this happens before the function call")
        print(function)
        return_value = function(*args, **kwargs)
        print("this happens after the function call")
        return return_value

    return inner


@decorator
def multiply(a, b):
    return a * b


print(multiply)
print(multiply(5, 6))


@contextmanager
def scope():
    print("this happens before the with block")
    yield True
    print("this happens after the with block")


with scope() as value:
    print(value)
