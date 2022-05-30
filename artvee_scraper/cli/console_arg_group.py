import argparse

from artvee_scraper.writer.writer_factory import WriterType

from .arg_group import ArgGroup


class JsonConsoleArgGroup(ArgGroup):
    """The group of command line arguments associated with the `JsonConsoleWriter`"""

    def __init__(self, subparsers: argparse._SubParsersAction) -> None:
        super().__init__(subparsers)

    def get_name(self) -> str:
        return WriterType.JSON_CONSOLE.writer_name

    def get_help(self) -> str:
        return WriterType.JSON_CONSOLE.description

    def add_arguments(self, subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--space-level",
            dest="space_level",
            default=0,
            choices=range(2, 7),
            metavar="[2-6]",
            help="Enable pretty-printing; number of spaces to indent (2-6)",
            type=int,
        )
        subparser.add_argument(
            "--sort-keys",
            dest="sort_keys",
            action="store_true",
            help="Sort JSON keys in alphabetical order",
        )
        subparser.add_argument(
            "--include-image",
            dest="include_image",
            action="store_true",
            help="Include image bytes in the output",
        )
