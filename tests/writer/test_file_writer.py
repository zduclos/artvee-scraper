import builtins
import logging
import os
import textwrap
from io import BytesIO, StringIO

from artwork import Artwork
from mockito import ANY, unstub, verify, when

from writer.file_writer import JsonFileWriter, MultiFileWriter


def get_artwork() -> Artwork:
    return Artwork(
        url="https://artvee.com/dl/composition-no-23/",
        title="Composition no. 23",
        category="Abstract",
        artist="Jacoba van Heemskerck",
        date="1915",
        origin="Dutch, 1876 - 1923",
        image=bytes.fromhex("CAFEBABE"),
    )


class InMemoryTextFile(StringIO):
    def __init__(self, initial_value=""):
        super().__init__(initial_value)

    def close(self):
        # No-op; override to prevent memory buffer from being discarded
        pass

    def dispose(self):
        super().close()


class InMemoryBytesFile(BytesIO):
    def __init__(self, initial_bytes=b""):
        super().__init__(initial_bytes)

    def close(self):
        # No-op; override to prevent memory buffer from being discarded
        pass

    def dispose(self):
        super().close()


def test_json_file_writer_write():
    # Mock open
    in_memory_file = InMemoryTextFile()
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenReturn(in_memory_file)

    # Setup
    writer = JsonFileWriter("/tmp")
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"
        assert (
            in_memory_file.getvalue()
            == '{"url": "https://artvee.com/dl/composition-no-23/", "title": "Composition no. 23", "category": "Abstract", "artist": "Jacoba van Heemskerck", "date": "1915", "origin": "Dutch, 1876 - 1923", "image": "yv66vg=="}'
        )

        verify(builtins, times=1).open(...)
    finally:
        # Cleanup
        in_memory_file.dispose()
        unstub()


def test_json_file_writer_write_exception():
    # Mock open
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenRaise(
        FileExistsError("file already exists!")
    )

    # Setup
    writer = JsonFileWriter("/tmp")
    artwork = get_artwork()

    # Test
    result = writer.write(artwork)

    # Validate
    assert result is False, "Write return value is invalid"

    verify(builtins, times=1).open(...)

    # Cleanup
    unstub()


def test_json_file_writer_sort_keys():
    # Mock open
    in_memory_file = InMemoryTextFile()
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenReturn(in_memory_file)

    # Setup
    writer = JsonFileWriter("/tmp", sort_keys=True)
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"
        assert (
            in_memory_file.getvalue()
            == '{"artist": "Jacoba van Heemskerck", "category": "Abstract", "date": "1915", "image": "yv66vg==", "origin": "Dutch, 1876 - 1923", "title": "Composition no. 23", "url": "https://artvee.com/dl/composition-no-23/"}'
        )

        verify(builtins, times=1).open(...)
    finally:
        # Cleanup
        in_memory_file.dispose()
        unstub()


def test_json_file_writer_space_level():
    # Mock open
    in_memory_file = InMemoryTextFile()
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenReturn(in_memory_file)

    # Setup
    writer = JsonFileWriter("/tmp", space_level=2)
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"

        expected_json_str = """\
        {
          "url": "https://artvee.com/dl/composition-no-23/",
          "title": "Composition no. 23",
          "category": "Abstract",
          "artist": "Jacoba van Heemskerck",
          "date": "1915",
          "origin": "Dutch, 1876 - 1923",
          "image": "yv66vg=="
        }"""
        assert in_memory_file.getvalue() == textwrap.dedent(expected_json_str)

        verify(builtins, times=1).open(...)
    finally:
        # Cleanup
        in_memory_file.dispose()
        unstub()


def test_json_file_writer_overwrite_existing():
    # Mock open
    when(builtins).open(ANY(str), "w", encoding="UTF-8").thenReturn(StringIO())

    # Setup
    writer = JsonFileWriter("/tmp", overwrite_existing=True)
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"

        verify(builtins, times=1).open(...)
    finally:
        # Cleanup
        unstub()


def test_multi_file_writer_write():
    # Mock open (image write)
    in_memory_image_file = InMemoryBytesFile()
    when(builtins).open(ANY(str), "xb", encoding="UTF-8").thenReturn(
        in_memory_image_file
    )

    # Mock open (metadata write)
    in_memory_meta_file = InMemoryTextFile()
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenReturn(in_memory_meta_file)

    # Setup
    writer = MultiFileWriter("/tmp/metadata", "/tmp/images")
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"
        assert in_memory_image_file.getvalue() == b"\xca\xfe\xba\xbe"
        assert (
            in_memory_meta_file.getvalue()
            == '{"url": "https://artvee.com/dl/composition-no-23/", "title": "Composition no. 23", "category": "Abstract", "artist": "Jacoba van Heemskerck", "date": "1915", "origin": "Dutch, 1876 - 1923"}'
        )

        verify(builtins, times=2).open(...)

    finally:
        # Cleanup
        in_memory_image_file.dispose()
        in_memory_meta_file.dispose()
        unstub()


def test_multi_file_write_metadata_rollback():
    # Mock open (image write)
    in_memory_image_file = BytesIO()  # no need to capture; automatically discards
    when(builtins).open(ANY(str), "xb", encoding="UTF-8").thenReturn(
        in_memory_image_file
    )

    # Mock open (metadata write)
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenRaise(
        FileExistsError("file already exists!")
    )

    # Mock os::remove
    when(os).remove(...).thenReturn(None)

    # Setup
    writer = MultiFileWriter("/tmp/metadata", "/tmp/images")
    artwork = get_artwork()

    # Test
    result = writer.write(artwork)

    # Validate
    assert result is False, "Write return value is invalid"
    verify(builtins, times=2).open(...)
    verify(os, times=1).remove(...)

    # Cleanup
    unstub()


def test_multi_file_write_image_rollback():
    # Mock open (image write)
    when(builtins).open(ANY(str), "xb", encoding="UTF-8").thenRaise(
        FileExistsError("file already exists!")
    )

    # Mock os::remove
    when(os).remove(...).thenReturn(None)

    # Setup
    writer = MultiFileWriter("/tmp/metadata", "/tmp/images")
    artwork = get_artwork()

    # Test
    result = writer.write(artwork)

    # Validate
    assert result is False, "Write return value is invalid"
    verify(builtins, times=1).open(...)
    verify(os, times=0).remove(...)

    # Cleanup
    unstub()


def test_multi_file_writer_sort_keys():
    # Mock open (image write)
    in_memory_image_file = InMemoryBytesFile()
    when(builtins).open(ANY(str), "xb", encoding="UTF-8").thenReturn(
        in_memory_image_file
    )

    # Mock open (metadata write)
    in_memory_meta_file = InMemoryTextFile()
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenReturn(in_memory_meta_file)

    # Setup
    writer = MultiFileWriter("/tmp/metadata", "/tmp/images", sort_keys=True)
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"
        assert in_memory_image_file.getvalue() == b"\xca\xfe\xba\xbe"
        assert (
            in_memory_meta_file.getvalue()
            == '{"artist": "Jacoba van Heemskerck", "category": "Abstract", "date": "1915", "origin": "Dutch, 1876 - 1923", "title": "Composition no. 23", "url": "https://artvee.com/dl/composition-no-23/"}'
        )

        verify(builtins, times=2).open(...)

    finally:
        # Cleanup
        in_memory_image_file.dispose()
        in_memory_meta_file.dispose()
        unstub()


def test_multi_file_writer_space_level():
    # Mock open (image write)
    in_memory_image_file = InMemoryBytesFile()
    when(builtins).open(ANY(str), "xb", encoding="UTF-8").thenReturn(
        in_memory_image_file
    )

    # Mock open (metadata write)
    in_memory_meta_file = InMemoryTextFile()
    when(builtins).open(ANY(str), "x", encoding="UTF-8").thenReturn(in_memory_meta_file)

    # Setup
    writer = MultiFileWriter("/tmp/metadata", "/tmp/images", space_level=2)
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"
        assert in_memory_image_file.getvalue() == b"\xca\xfe\xba\xbe"

        expected_json_str = """\
        {
          "url": "https://artvee.com/dl/composition-no-23/",
          "title": "Composition no. 23",
          "category": "Abstract",
          "artist": "Jacoba van Heemskerck",
          "date": "1915",
          "origin": "Dutch, 1876 - 1923"
        }"""
        assert in_memory_meta_file.getvalue() == textwrap.dedent(expected_json_str)

        verify(builtins, times=2).open(...)

    finally:
        # Cleanup
        in_memory_image_file.dispose()
        in_memory_meta_file.dispose()
        unstub()


def test_multi_file_writer_overwrite_existing():
    # Mock open (image write)
    when(builtins).open(ANY(str), "wb", encoding="UTF-8").thenReturn(BytesIO())

    # Mock open (metadata write)
    when(builtins).open(ANY(str), "w", encoding="UTF-8").thenReturn(StringIO())

    # Setup
    writer = MultiFileWriter("/tmp/metadata", "/tmp/images", overwrite_existing=True)
    artwork = get_artwork()

    try:
        # Test
        result = writer.write(artwork)

        # Validate
        assert result is True, "Write return value is invalid"

        verify(builtins, times=2).open(...)

    finally:
        # Cleanup
        unstub()
