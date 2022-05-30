from typing import List, Any
import copy


class ListIterator:
    """Iterate a list in either direction.

    The iterator works on a snapshot of `elements` by using a deep copy during construction.
    Changes to `elements` will not be reflected while iterating.

    Attributes:
        elements (List[Any]):
            List of elements to iterate.
        index (int, optional)
            Set the cursor to a specified index. Defaults to 0.
    """

    def __init__(self, elements: List[Any], index: int = 0):
        self._elements = copy.deepcopy(elements)
        self._cursor = index

    def has_previous(self) -> bool:
        """Determine if more elements exist in the backward direction.

        Returns:
            `True` if more elements exist; otherwise `False`.
        """
        return self._cursor != 0

    def has_next(self) -> bool:
        """Determine if more elements exist in the forward direction.

        Returns:
            `True` if more elements exist; otherwise `False`.
        """
        return self._cursor != len(self._elements)

    def next_index(self) -> int:
        """Returns the index which would be returned by a call to `next()`.

        Returns:
            Next index, or `len(elements)` if no next element exists.
        """
        return self._cursor

    def previous_index(self) -> int:
        """Returns the index which would be returned by a call to `previous()`.

        Returns:
            Previous index, or `-1` if no previous element exists.
        """
        return self._cursor - 1

    def next(self) -> Any:
        """Returns the next element and moves the cursor forward.

        Returns:
            The next element.
        Raises:
            IndexError: If no next element exists
        """
        i = self._cursor
        if i >= len(self._elements):
            raise IndexError()

        self._cursor = i + 1
        return self._elements[i]

    def previous(self) -> Any:
        """Returns the previous element and moves the cursor backward.

        Returns:
            The previous element.
        Raises:
            IndexError: If no next element exists
        """
        i = self._cursor - 1
        if i < 0:
            raise IndexError()

        self._cursor = i
        return self._elements[i]
