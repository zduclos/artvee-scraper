import argparse
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from artvee_scraper.scraper import CategoryType


class ArgGroup(ABC):
    """The abstract group of command line arguments for this command.

    Attributes:
        subparsers (argparse._SubParsersAction): Action object used to create subparsers.
    """

    def __init__(self, subparsers: argparse._SubParsersAction) -> None:
        """Constructs a new `ArgGroup` instance."""
        self.subparsers = subparsers

    @abstractmethod
    def get_name(self) -> str:
        """Returns the argument group name.

        Returns:
            The argument group name.

        Raises:
            NotImplementedError: If the derived class does not override this method
        """
        raise NotImplementedError

    @abstractmethod
    def get_help(self) -> str:
        """Returns the help message for this argument group.

        Returns:
            The argument group help message.

        Raises:
            NotImplementedError: If the derived class does not override this method
        """
        raise NotImplementedError

    @abstractmethod
    def add_arguments(self, subparser: argparse.ArgumentParser) -> None:
        """Populates the subparser with command line arguments associated with this group.

        Args:
            subparser: Argument subparser to populate with command line arguments.

        Raises:
            NotImplementedError: If the derived class does not override this method.
        """
        raise NotImplementedError

    def get_description(self) -> Optional[str]:
        """Brief description of this argument group.

        Returns:
            The argument group description.
        """
        pass

    def register(self) -> argparse.ArgumentParser:
        """Creates a subparser for this command with command-line arguments defined.

        Note: A command may only be registered once; a duplicate will overwrite the previous registration.

        Returns:
            The argument subparser created for this command.
        """
        subparser = self.subparsers.add_parser(
            self.get_name(), help=self.get_help(), description=self.get_description()
        )
        subparser.set_defaults(command=self.get_name())

        # Populate subparser with required program arguments
        ArgGroup._add_program_args(subparser)
        # Populate subparser with command specific arguments
        self.add_arguments(subparser)

        return subparser

    @staticmethod
    def _add_program_args(subparser: argparse.ArgumentParser) -> None:
        """Populates the subparser with required program arguments.

        Args:
            subparser: Argument subparser to populate with command line arguments.
        """
        subparser.add_argument(
            "-t",
            "--worker-threads",
            dest="worker_threads",
            default=3,
            action=IsInRangeAction,
            metavar="[1-16]",
            help="Number of worker threads (1-16)",
            type=int,
            minInclusive=1,
            maxInclusive=16,
        )
        subparser.add_argument(
            "-l",
            "--log-level",
            dest="log_level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Set the application log level",
        )
        subparser.add_argument(
            "-c",
            "--category",
            dest="categories",
            action="append",
            type=CategoryType,
            choices=list(CategoryType),
            help="Category of artwork to scrape",
        )

        log_file_group = subparser.add_argument_group(
            'optional log file arguments')
        log_file_group.add_argument(
            "--log-dir",
            dest="log_dir",
            action=IsDirAction,
            help="Log file output directory",
        )
        log_file_group.add_argument(
            "--log-max-size",
            dest="log_max_size_mb",
            default=1024,  # 1 GB
            action=IsInRangeAction,  # 1MB to 10 GB
            metavar="[1-10240]",
            help="Maximum log file size in MB (1-10,240)",
            type=int,
            minInclusive=1,
            maxInclusive=10240,
        )
        log_file_group.add_argument(
            "--log-max-backups",
            dest="log_max_backups",
            default=10,
            action=IsInRangeAction,
            metavar="[0-100]",
            help="Maximum number of log files to keep (0-100)",
            type=int,
            minInclusive=0,
            maxInclusive=100,
        )


class IsInRangeAction(argparse.Action):
    def __init__(self, minInclusive: int, maxInclusive: int, *args, **kwargs):
        self.minInclusive = minInclusive
        self.maxInclusive = maxInclusive
        super(IsInRangeAction, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        if not value in range(self.minInclusive, self.maxInclusive + 1):
            parser.error(
                f"argument {option_string}: invalid choice: {value} (must be in range [{self.minInclusive}-{self.maxInclusive}])")

        setattr(namespace, self.dest, value)


class IsDirAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        path = Path(value)

        if not path.is_dir():
            parser.error(
                f"argument {option_string}: invalid choice: A directory in the path {value} does not exist")

        setattr(namespace, self.dest, value)
