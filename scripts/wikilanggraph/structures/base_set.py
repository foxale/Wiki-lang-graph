__all__ = ["BaseSet"]

from collections import Hashable
from collections import Iterable
from collections import MutableSet


class BaseSet(Hashable, MutableSet):
    __hash__ = MutableSet._hash

    def __init__(self, iterable: Iterable = ()):
        self._data = set(iterable)

    def __contains__(self, value):
        return value in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def add(self, item):
        self._data.add(item)

    def discard(self, item):
        self._data.discard(item)
