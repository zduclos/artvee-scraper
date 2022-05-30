from argparse import Namespace

import pytest

from writer import writer_factory
from writer.abstract_writer import AbstractWriter
from writer.console_writer import JsonConsoleWriter
from writer.file_writer import JsonFileWriter, MultiFileWriter


@pytest.mark.parametrize(
    "command, args, cls",
    [
        (
            "file-json",
            Namespace(
                space_level=2, sort_keys=True, overwrite_existing=True, dir_path="/tmp"
            ),
            JsonFileWriter,
        ),
        (
            "file-multi",
            Namespace(
                space_level=2,
                sort_keys=True,
                overwrite_existing=True,
                metadata_dir_path="/tmp",
                image_dir_path="/tmp",
            ),
            MultiFileWriter,
        ),
        (
            "console-json",
            Namespace(space_level=2, sort_keys=True, include_image=True),
            JsonConsoleWriter,
        ),
    ],
)
def test_get_instance(command, args, cls):
    # Test
    writer = writer_factory.get_instance(command, args)

    # Validate
    assert isinstance(writer, cls)
    assert isinstance(writer, AbstractWriter)


def test_get_instance_exception():
    # Setup
    args = Namespace(space_level=2, sort_keys=True, include_image=True)

    # Test
    with pytest.raises(ValueError):
        writer_factory.get_instance("invalid_command", args)
