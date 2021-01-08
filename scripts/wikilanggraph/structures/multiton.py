from functools import wraps


def multiton(*keys):
    def _multiton(cls):
        @wraps(cls)
        def getinstance(**kwargs):
            key = tuple(v for k, v in kwargs.items() if k in keys)
            if key not in cls._instances:
                cls._instances[key] = cls(**kwargs)
            return cls._instances[key]

        return getinstance

    return _multiton
