import argparse
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from artvee_scraper.cli.log_arg_group import JsonLogArgGroup
from artvee_scraper.cli.file_arg_group import (JsonFileArgGroup,
                                               MultiFileArgGroup)
from artvee_scraper.writer import writer_factory

from .scraper import ArtveeScraper, CategoryType, ImageSize


def parse_cli_args() -> argparse.Namespace:
    arg_parser = argparse.ArgumentParser(
        description="Scrape artwork from https://www.artvee.com"
    )
    subparsers = arg_parser.add_subparsers()

    # Register command options & parameters
    JsonLogArgGroup(subparsers).register()
    JsonFileArgGroup(subparsers).register()
    MultiFileArgGroup(subparsers).register()

    # Check that a command has been provided
    if len(sys.argv) == 1:
        arg_parser.print_help()
        arg_parser.exit()

    return arg_parser.parse_args()


def get_logger(args: argparse.Namespace) -> logging.Logger:
    handlers = None
    if log_dir := args.log_dir:
        log_file = f"{log_dir}{os.path.sep}artvee_scraper.log"
        log_max_bytes = args.log_max_size_mb * pow(1024, 2)

        rotating_file_appender = RotatingFileHandler(
            log_file, mode='a', maxBytes=log_max_bytes, backupCount=args.log_max_backups, encoding=None, delay=0)
        handlers = [rotating_file_appender]

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] %(module)s.%(funcName)s(%(lineno)d) | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )

    return logging.getLogger("artvee-scraper")


def main():
    args = parse_cli_args()
    logger = get_logger(args)

    logger.debug(f"Parsed command line arguments: {vars(args)}")
    writer = writer_factory.get_instance(args.command, args)

    # Remove any duplicate categories if specified
    categories = (
        list(dict.fromkeys(args.categories)
             ) if args.categories else list(CategoryType)
    )
    scraper = ArtveeScraper(
        writer,
        worker_threads=args.worker_threads,
        categories=sorted(categories),
    )

    try:
        with scraper as s:
            s.start()
    except KeyboardInterrupt:
        raise SystemExit(
            "Keyboard interrupt detected; shutting down immediately...")


main()
