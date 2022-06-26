import argparse

from artvee_scraper.writer.writer_factory import WriterType

from .arg_group import ArgGroup, IsDirAction, IsInRangeAction


class JsonFileArgGroup(ArgGroup):
    """The group of command line arguments associated with the `JsonFileWriter`"""

    def __init__(self, subparsers: argparse._SubParsersAction) -> None:
        super().__init__(subparsers)

    def get_name(self) -> str:
        return WriterType.JSON_FILE.writer_name

    def get_help(self) -> str:
        return WriterType.JSON_FILE.description

    def add_arguments(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "dir_path", action=IsDirAction, help="JSON file output directory"
        )
        subparser.add_argument(
            "--space-level",
            dest="space_level",
            default=0,
            action=IsInRangeAction,
            metavar="[2-6]",
            help="Enable pretty-printing; number of spaces to indent (2-6)",
            type=int,
            minInclusive=2,
            maxInclusive=6,
        )
        subparser.add_argument(
            "--sort-keys",
            dest="sort_keys",
            action="store_true",
            help="Sort JSON keys in alphabetical order",
        )
        subparser.add_argument(
            "--overwrite-existing",
            dest="overwrite_existing",
            action="store_true",
            help="Overwrite existing files",
        )


class MultiFileArgGroup(ArgGroup):
    """The group of command line arguments associated with the `MultiFileWriter`"""

    def __init__(self, subparsers: argparse._SubParsersAction) -> None:
        super().__init__(subparsers)

    def get_name(self) -> str:
        return WriterType.MULTI_FILE.writer_name

    def get_help(self) -> str:
        return WriterType.MULTI_FILE.description

    def add_arguments(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "metadata_dir_path",
            action=IsDirAction,
            help="Image metadata file output directory",
        )
        subparser.add_argument(
            "image_dir_path",
            action=IsDirAction,
            help="Downloaded image file output directory",
        )
        subparser.add_argument(
            "--space-level",
            dest="space_level",
            default=0,
            action=IsInRangeAction,
            metavar="[2-6]",
            help="Enable pretty-printing; number of spaces to indent (2-6)",
            type=int,
            minInclusive=2,
            maxInclusive=6,
        )
        subparser.add_argument(
            "--sort-keys",
            dest="sort_keys",
            action="store_true",
            help="Sort JSON keys in alphabetical order",
        )
        subparser.add_argument(
            "--overwrite-existing",
            dest="overwrite_existing",
            action="store_true",
            help="Overwrite existing files",
        )
