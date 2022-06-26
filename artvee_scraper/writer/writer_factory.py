from __future__ import annotations

from argparse import Namespace
from enum import Enum
from typing import Callable, Optional

from .abstract_writer import AbstractWriter
from .log_writer import JsonLogWriter
from .file_writer import JsonFileWriter, MultiFileWriter


def get_instance(command_name: str, args: Namespace) -> AbstractWriter:
    """Factory for creating instances of classes derived from `AbstractWriter`.

    Args:
        command_name:
            Name of the writer to create.

    Returns:
        A newly constructed writer instance.

    Raises:
        ValueError: If the `WriterType` specified by `command_name` does not exist
    """
    if writer_type := WriterType.from_str(command_name):
        creator_fn = writer_type.creator
        return creator_fn(args)

    raise ValueError(command_name)


class WriterType(Enum):
    """Represents an artistic work.

    Attributes:
        writer_name (str):
            Command name for this writer
        description (str):
            A brief description of this writer
        creator (Callable[[Namespace], AbstractWriter]):
            Function used to create a writer instance from arguments
    """

    JSON_FILE = (
        "file-json",
        "Artwork is represented as a JSON object and written to a file",
        lambda args: JsonFileWriter(
            args.dir_path,
            space_level=args.space_level,
            sort_keys=args.sort_keys,
            overwrite_existing=args.overwrite_existing,
        ),
    )
    MULTI_FILE = (
        "file-multi",
        "Artwork image and metadata are written as separate files",
        lambda args: MultiFileWriter(
            args.metadata_dir_path,
            args.image_dir_path,
            space_level=args.space_level,
            sort_keys=args.sort_keys,
            overwrite_existing=args.overwrite_existing,
        ),
    )
    JSON_LOG = (
        "log-json",
        "Artwork is output to the log as a JSON object",
        lambda args: JsonLogWriter(
            space_level=args.space_level,
            sort_keys=args.sort_keys,
            include_image=args.include_image,
        ),
    )

    def __init__(
        self,
        writer_name: str,
        description: str,
        creator: Callable[[Namespace], AbstractWriter],
    ) -> None:
        """Constructs a new `WriterType` enum instance."""
        self.writer_name = writer_name
        self.description = description
        self.creator = creator

    @staticmethod
    def from_str(writer_name: str) -> Optional[WriterType]:
        """Convenience method to return the `WriterType` enum member associated with the `writer_name`.

        Args:
            writer_name:
                Name of the enum member to retrieve.

        Returns:
            The associated `WriterType` enum member or `None` if it does not exist.
        """
        for writer in WriterType:
            if writer.writer_name == writer_name:
                return writer

        return None
