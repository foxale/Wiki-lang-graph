__all__ = ["mergedicts"]


class OverwriteException(Exception):
    pass


def mergedicts(d1: dict, d2: dict):
    for k in d1.keys() | d2.keys():
        if k in d1 and k in d2:
            if isinstance(d1[k], dict) and isinstance(d2[k], dict):
                yield k, dict(mergedicts(d1[k], d2[k]))
            elif isinstance(d1[k], list) and isinstance(d2[k], list):
                yield k, d1[k] + d2[k]
            elif d1[k] == d2[k]:
                yield k, d1[k]
            else:
                raise OverwriteException(
                    "Some elements would be overwritten during this operation: %s, %s",
                    d1[k],
                    d2[k],
                )
        elif k in d1:
            yield k, d1[k]
        else:
            yield k, d2[k]
