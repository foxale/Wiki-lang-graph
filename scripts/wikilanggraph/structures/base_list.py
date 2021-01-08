__all__ = ["BaseList"]

from collections import Iterable
from collections import Sequence
from typing import Optional


class BaseList(Sequence):
    def __init__(self, iterable: Optional[Iterable] = ()):
        self._data = []
        if iterable is not None:
            if type(iterable) == type(self._data):
                self._data[:] = iterable
            elif isinstance(iterable, BaseList):
                self._data[:] = iterable._data[:]
            else:
                self._data = list(iterable)

    def __contains__(self, value):
        return value in self._data

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return repr(self._data)

    def __getitem__(self, idx_or_name):
        return self._data[idx_or_name]

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["_data"] = self.__dict__["_data"][:]
        return inst

    def append(self, item):
        self._data.append(item)

    def insert(self, i, item):
        self._data.insert(i, item)

    def pop(self, i=-1):
        return self._data.pop(i)

    def remove(self, item):
        self._data.remove(item)

    def clear(self):
        self._data.clear()

    def copy(self):
        return self.__class__(self)

    def count(self, item):
        return self._data.count(item)

    def index(self, item, *args):
        return self._data.index(item, *args)

    def reverse(self):
        self._data.reverse()

    def sort(self, /, *args, **kwds):
        self._data.sort(*args, **kwds)

    def extend(self, other):
        if isinstance(other, BaseList):
            self._data.extend(other._data)
        else:
            self._data.extend(other)

    def __lt__(self, other):
        return self._data < self.__cast(other)

    def __le__(self, other):
        return self._data <= self.__cast(other)

    def __eq__(self, other):
        return self._data == self.__cast(other)

    def __gt__(self, other):
        return self._data > self.__cast(other)

    def __ge__(self, other):
        return self._data >= self.__cast(other)

    def __cast(self, other):
        return other._data if isinstance(other, BaseList) else other

    def __setitem__(self, i, item):
        self._data[i] = item

    def __delitem__(self, i):
        del self._data[i]

    def __add__(self, other):
        if isinstance(other, BaseList):
            return self.__class__(self._data + other._data)
        elif isinstance(other, type(self._data)):
            return self.__class__(self._data + other)
        return self.__class__(self._data + list(other))

    def __radd__(self, other):
        if isinstance(other, BaseList):
            return self.__class__(other._data + self._data)
        elif isinstance(other, type(self._data)):
            return self.__class__(other + self._data)
        return self.__class__(list(other) + self._data)

    def __iadd__(self, other):
        if isinstance(other, BaseList):
            self._data += other._data
        elif isinstance(other, type(self._data)):
            self._data += other
        else:
            self._data += list(other)
        return self

    def __mul__(self, n):
        return self.__class__(self._data * n)

    __rmul__ = __mul__

    def __imul__(self, n):
        self._data *= n
        return self
