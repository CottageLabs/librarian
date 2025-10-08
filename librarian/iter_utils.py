from itertools import tee
from typing import Iterable, Callable


def peek(values: Iterable):
    a, b = tee(values)
    first = next(b, None)
    return first


def remove_duplicate(val_list: Iterable, id_fn: Callable = None, ) -> Iterable:
    """
    remove duplicate and keep order and keep generator

    >>> list(remove_duplicate([1, 2,4,2, 1, 1, 3]))
    [1, 2, 4, 3]

    Parameters
    ----------
    val_list
    id_fn

    Returns
    -------

    """
    return RemoveDuplicate(id_fn).remove(val_list)


class RemoveDuplicate:
    def __init__(self, id_fn: Callable = None):
        self.used_id = set()
        self.id_fn = id_fn

    def remove(self, val_list: Iterable) -> Iterable:
        for v in val_list:
            _id = v if self.id_fn is None else self.id_fn(v)
            if _id not in self.used_id:
                self.used_id.add(_id)
                yield v
