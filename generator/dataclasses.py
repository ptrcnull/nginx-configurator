# a very primitive polyfill for dataclasses 3.7 module which makes coding easier
# but most Linux servers ship with 3.6 and upgrading it is a mess sooo...


def dataclass(cls):
    def __init__(self, **kwargs):
        for param in kwargs:
            setattr(self, param, kwargs.get(param))

    def __str__(self):
        return str(self.__dict__)

    cls.__init__ = __init__
    cls.__str__ = __str__
    return cls
