from utils import ListIterator
import pytest


def test_listiterator_has_next():
    # Setup
    l = [1]
    iter = ListIterator(l)

    # Test
    result = iter.has_next()

    # Validate
    assert result == True, "Has next should be true"


def test_listiterator_has_next_failure():
    # Setup
    l = []
    iter = ListIterator(l)

    # Test
    result = iter.has_next()

    # Validate
    assert result == False, "Has next should be false"


def test_listiterator_has_previous():
    # Setup
    l = [1]
    iter = ListIterator(l, 1)  # move the cursor to the end

    # Test
    result = iter.has_previous()

    # Validate
    assert result == True, "Has previous does not match expected value"


def test_listiterator_has_previous_failure():
    # Setup
    l = []
    iter = ListIterator(l)

    # Test
    result = iter.has_previous()

    # Validate
    assert result == False, "Has previous does not match expected value"


def test_listiterator_next_index():
    # Setup
    l = ["test"]
    iter = ListIterator(l, 1)  # move the cursor to the end

    # Test
    result = iter.next_index()

    # Validate
    assert result == 1, "Next index does not match expected value"


def test_listiterator_next_index_failure():
    # Setup
    l = ["test"]
    iter = ListIterator(l)

    # Test
    result = iter.next_index()

    # Validate
    assert result == 0, "Next index does not match expected value"


def test_listiterator_prev_index():
    # Setup
    l = ["test"]
    iter = ListIterator(l, 1)  # move the cursor to the end

    # Test
    result = iter.previous_index()

    # Validate
    assert result == 0, "Previous index does not match expected value"


def test_listiterator_prev_index_failure():
    # Setup
    l = ["test"]
    iter = ListIterator(l)

    # Test
    result = iter.previous_index()

    # Validate
    assert result == -1, "Previous index does not match expected value"


def test_listiterator_next():
    # Setup
    l = ["test"]
    iter = ListIterator(l)

    # Test
    result = iter.next()

    # Validate
    assert result == "test", "Next element does not match expected value"


def test_listiterator_previous():
    # Setup
    l = ["test"]
    iter = ListIterator(l, 1)  # move the cursor to the end

    # Test
    result = iter.previous()

    # Validate
    assert result == "test", "Previous element does not match expected value"


def test_listiterator_next_exception():
    # Setup
    l = []
    iter = ListIterator(l)

    # Test
    with pytest.raises(IndexError):
        iter.next()


def test_listiterator_previous_exception():
    # Setup
    l = []
    iter = ListIterator(l)

    # Test
    with pytest.raises(IndexError):
        iter.previous()


def test_listiterator_snapshot():
    # Setup
    l = ["test"]
    iter = ListIterator(l)  # iterator is based on a snapshot of original list
    l.extend(["can", "modify", "iterator", "?"])

    # Test
    count = 0
    while iter.has_next():
        iter.next()
        count += 1

    # Validate
    assert count == 1, "Iterator elements should not be modified"
