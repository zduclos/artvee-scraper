import argparse

from artvee_scraper.writer.writer_factory import WriterType

from .arg_group import ArgGroup, IsInRangeAction


class JsonLogArgGroup(ArgGroup):
    """The group of command line arguments associated with the `JsonLogWriter`"""

    def __init__(self, subparsers: argparse._SubParsersAction) -> None:
        super().__init__(subparsers)

    def get_name(self) -> str:
        return WriterType.JSON_LOG.writer_name

    def get_help(self) -> str:
        return WriterType.JSON_LOG.description

    def add_arguments(self, subparser: argparse.ArgumentParser) -> None:
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
            "--include-image",
            dest="include_image",
            action="store_true",
            help="Include image bytes in the output",
        )
