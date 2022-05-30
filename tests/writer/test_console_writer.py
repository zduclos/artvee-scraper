import logging
import textwrap

from artwork import Artwork
from mockito import mock, verify, when

from writer.console_writer import JsonConsoleWriter


def test_json_console_writer_write(caplog):
    # Setup
    writer = JsonConsoleWriter()
    artwork = Artwork(
        url="https://artvee.com/dl/composition-no-23/",
        title="Composition no. 23",
        category="Abstract",
        artist="Jacoba van Heemskerck",
        date="1915",
        origin="Dutch, 1876 - 1923",
    )

    # Test
    with caplog.at_level(logging.INFO):
        result = writer.write(artwork)

    # Verify
    assert result is True, "Write return value is invalid"
    assert (
        caplog.records[-1].message
        == '{"url": "https://artvee.com/dl/composition-no-23/", "title": "Composition no. 23", "category": "Abstract", "artist": "Jacoba van Heemskerck", "date": "1915", "origin": "Dutch, 1876 - 1923", "image": null}'
    )
    assert caplog.records[-1].levelname == "INFO"


def test_json_console_writer_include_image(caplog):
    # Setup
    writer = JsonConsoleWriter(include_image=True)
    artwork = Artwork(
        url="https://artvee.com/dl/composition-no-23/",
        title="Composition no. 23",
        category="Abstract",
        artist="Jacoba van Heemskerck",
        date="1915",
        origin="Dutch, 1876 - 1923",
        image=bytes.fromhex("CAFEBABE"),
    )

    # Test
    with caplog.at_level(logging.INFO):
        result = writer.write(artwork)

    # Verify
    assert result is True, "Write return value is invalid"
    assert (
        caplog.records[-1].message
        == '{"url": "https://artvee.com/dl/composition-no-23/", "title": "Composition no. 23", "category": "Abstract", "artist": "Jacoba van Heemskerck", "date": "1915", "origin": "Dutch, 1876 - 1923", "image": "yv66vg=="}'
    )
    assert caplog.records[-1].levelname == "INFO"


def test_json_console_writer_sort_keys(caplog):
    # Setup
    writer = JsonConsoleWriter(sort_keys=True)
    artwork = Artwork(
        url="https://artvee.com/dl/composition-no-23/",
        title="Composition no. 23",
        category="Abstract",
        artist="Jacoba van Heemskerck",
        date="1915",
        origin="Dutch, 1876 - 1923",
    )

    # Test
    with caplog.at_level(logging.INFO):
        result = writer.write(artwork)

    # Verify
    assert result is True, "Write return value is invalid"
    assert (
        caplog.records[-1].message
        == '{"artist": "Jacoba van Heemskerck", "category": "Abstract", "date": "1915", "image": null, "origin": "Dutch, 1876 - 1923", "title": "Composition no. 23", "url": "https://artvee.com/dl/composition-no-23/"}'
    )
    assert caplog.records[-1].levelname == "INFO"


def test_json_console_writer_space_level(caplog):
    # Setup
    writer = JsonConsoleWriter(space_level=2)
    artwork = Artwork(
        url="https://artvee.com/dl/composition-no-23/",
        title="Composition no. 23",
        category="Abstract",
        artist="Jacoba van Heemskerck",
        date="1915",
        origin="Dutch, 1876 - 1923",
    )

    # Test
    with caplog.at_level(logging.INFO):
        result = writer.write(artwork)

    # Verify
    assert result is True, "Write return value is invalid"
    assert caplog.records[-1].levelname == "INFO"

    expected_json_str = """\
    {
      "url": "https://artvee.com/dl/composition-no-23/",
      "title": "Composition no. 23",
      "category": "Abstract",
      "artist": "Jacoba van Heemskerck",
      "date": "1915",
      "origin": "Dutch, 1876 - 1923",
      "image": null
    }"""
    assert caplog.records[-1].message == textwrap.dedent(expected_json_str)
