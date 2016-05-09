"""
Haskell-ish lazy-list in PYthon (without monads)

~list/sequence defined by a function which generates its values.

For Example, Fiboancci:
    fib ~= reduce(zipwith(+), initial=[0, 1])


@todo: Create some functionality to allow this to be based on a generator
@todo: Determine if __getitem__ on slice should return list or LazyList?
"""
import typing
import collections
import numbers


# Type-Definitions
IndexType = typing.Union[numbers.Integral, slice]
# InternalType should have constraint Hashable, but this raises TypeError("A single constraint is not allowed")
InternalType = typing.TypeVar('InternalType')
LazyFunction = typing.Callable[[typing.Sequence, Index], InternalType]


class LazyList(list):
    """
    Lazy-evaluates index values. Already generated values are stored in
    an internal data structure (in this case, the one from default list class).

    The present form of this will only work for a recursive-ish function.
    This LazyFunction must be passed into the constructor, and must be a
    pure function on the current internal cached state, and the index to be
    retreived.

    I don't see any clear way to adapt LazyList to working on a generator.

    Maybe fix:
        In __getitem__, instead of 'if index >= len(self)', use 'except IndexError:',
        and
    """
    def __init__(self, function: LazyFunction, initial: typing.Sequence=()):
        self.function = function
        list.__init__(self, initial)

    def __setitem__(self, index: IndexType, value: InternalType) -> None:
        """Automatically extend internal list so 'Index' makes sense."""
        if isinstance(index, numbers.Integral):
            if index >= len(self):
                self.extend([None] * (index + 1 - len(self)))
            list.__setitem__(self, index, value)
        elif isinstance(index, slice):
            for _ind in _slice_range(index):
                self[_ind] = value
        else:
            raise TypeError("Invalid index type "+index.__class__.__name__)

    def __getitem__(self, index: IndexType) -> InternalType:
        """Create and cache results in internal list."""
        if isinstance(index, numbers.Integral):
            if index >= len(self):
                self[index] = self.function(self, index)
            return list.__getitem__(self, index)
        elif isinstance(index, slice):
            return [self[_ind] for _ind in _slice_range(index)]
        else:
            raise TypeError("Invalid index type "+index.__class__.__name__)

    def __str__(self) -> str:
        return str.format(
            "{klass}({cached_no_closing_bracket}, ... {func}(self, X)])",
            klass=self.__class__.__name__,
            cached_no_closing_bracket=list.__repr__(self)[:-1],
            func=self.function.__name__,
        )

    def __repr__(self) -> str:
        return str.format(
            "{cached_no_closing_bracket}, ...]",
            cached_no_closing_bracket=list.__repr__(self)[:-1]
        )

    def __iter__(self) -> typing.Iterator[InternalType]:
        yield from self.infinite()

    def finite(self) -> typing.Iterator[InternalType]:
        yield from list.__iter__(self)

    def infinite(self) -> typing.Iterator[InternalType]:
        yield from list.__iter__(self)
        counter = len(self) + 1
        while(True):
            yield self[counter]
            counter += 1


def _slice_range(_slice) -> range:
    return range(
        0 if _slice.start is None else _slice.start,
        _slice.stop,
        1 if _slice.step is None else _slice.step
    )








def test_lazy_list():
    def get_fib(seq, index):
        return seq[index-1] + seq[index-2]

    fib = LazyList(get_fib, [0, 1])

    slick = fib[0:2]
    ten = fib[:10]


    second = fib[2]
    inf = fib.infinite()
    five = [next(inf) for elm in range(5)]


    print()
    print("slick:", type(slick), slick)
    print()
    import ipdb
    ipdb.set_trace()
    print()

test_lazy_list()
