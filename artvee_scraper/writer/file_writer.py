import json
import logging
import os
from typing import Optional

from artvee_scraper.artwork import Artwork
from slugify import slugify

from .abstract_writer import AbstractWriter
from .command import Command, MacroCommand

logger = logging.getLogger("artvee-scraper")


class JsonFileWriter(AbstractWriter):
    """Class for writing an artwork to the filesystem as a JSON object.

    The artwork is written to the `dir_path` directory as a JSON object with the `.json` extension.

    Attributes:
        dir_path (str):
            Path to the output directory where the JSON file will be written.
        indent (int, optional):
            Enable pretty-printing; number of spaces to indent. Defaults to `0`.
        sort_keys (bool, optional):
            Sort the JSON keys in alphabetical order. Defaults to `False`.
        open_option (str):
            File mode to open the file for write access.
    """

    def __init__(
        self,
        dir_path: str,
        space_level: int = 0,
        sort_keys: bool = False,
        overwrite_existing: bool = False,
    ) -> None:
        self._dir_path = dir_path
        self._indent = space_level if space_level > 1 else None
        self._sort_keys = sort_keys
        self._open_option = "w" if overwrite_existing else "x"

    def write(self, artwork: Artwork) -> bool:
        """Writes the artwork as a JSON object to the filesystem.

        Args:
            artwork:
                Artistic work to be written to the filesystem.

        Returns:
            `True` if the artwork was written to the filesystem successfully; otherwise `False`.
        """
        try:
            # Create a clean base filename by converting to a slug
            slug = slugify(f"{artwork.artist}-{artwork.title}")

            file_path = f"{self._dir_path}{os.path.sep}{slug}.json"

            logger.debug("Writing %s to the filesystem", file_path)

            # Write file
            with open(file_path, self._open_option) as fout:
                json.dump(
                    artwork.to_dict(),
                    fout,
                    indent=self._indent,
                    sort_keys=self._sort_keys,
                    ensure_ascii=False,
                )
                logger.debug("Wrote %s to the filesystem", file_path)

            return True
        except Exception as fee:
            logger.error(
                "Failed to write %s to the filesystem; %s", file_path, fee)

        return False


class MultiFileWriter(AbstractWriter):
    """Class for writing an artwork to the filesystem as multiple files.

    The metadata is written to the `metadata_dir_path` directory as a JSON object with the `.json` extension.
    The image is written to the `image_dir_path` directory as bytes with the `.jpg` extension.

    Attributes:
        metadata_dir_path (str):
            Path to the output directory where the JSON metadata file will be written to.
        image_dir_path (str):
            Path to the output directory where the JPG image file will be written.
        indent (int, optional):
            Enable pretty-printing; number of spaces to indent. Defaults to `0`.
        sort_keys (bool, optional):
            Sort the JSON keys in alphabetical order. Defaults to `False`.
        overwrite_existing (bool, optional)
            Open the file for write access, overwriting if it already exists. Defaults to `False`
    """

    def __init__(
        self,
        metadata_dir_path: str,
        image_dir_path: str,
        space_level: int = 0,
        sort_keys: bool = False,
        overwrite_existing: bool = False,
    ) -> None:
        self._metadata_dir_path = metadata_dir_path
        self._image_dir_path = image_dir_path
        self._indent = space_level if space_level > 1 else None
        self._sort_keys = sort_keys
        self._overwrite_existing = overwrite_existing

    def write(self, artwork: Artwork) -> bool:
        """Writes the artwork and metadata as individual files.

        An attempt to rollback changes will be made in the event that both files cannot be written to the filesystem successfully.

        Args:
            artwork:
                Artistic work to be written to the filesystem.

        Returns:
            `True` if the artwork was written to the filesystem successfully; otherwise `False`.
        """
        macro_cmd = MacroCommand()
        macro_cmd.add(
            WriteImageCommand(self._image_dir_path, artwork,
                              self._overwrite_existing)
        )
        macro_cmd.add(
            WriteMetadataCommand(
                self._metadata_dir_path,
                artwork,
                self._indent,
                self._sort_keys,
                self._overwrite_existing,
            )
        )

        if not macro_cmd.execute():
            macro_cmd.revert()
            return False

        return True


class WriteImageCommand(Command):
    """Class for writing an artwork image to the filesystem.

    The image is written to the `path` directory as bytes with the `.jpg` extension.

    Attributes:
        image (bytes):
            JPG formatted image bytes.
        path (str):
            Path to the output directory where the JPG image file will be written.
        open_option (str):
            File mode to open the file for write access.
    """

    def __init__(
        self, dir_path: str, artwork: Artwork, overwrite_existing: bool
    ) -> None:
        """Constructs a new `WriteImageCommand` instance."""
        self._image = artwork.image

        # Create a clean base filename by converting to a slug
        slug = slugify(f"{artwork.artist}-{artwork.title}")
        self._path = f"{dir_path}{os.path.sep}{slug}.jpg"

        self._open_option = "wb" if overwrite_existing else "xb"

    def execute(self) -> bool:
        """Writes the artwork image to the filesystem.

        Returns:
            `True` if the image was written to the filesystem successfully; otherwise `False`.
        """
        if self._image:
            logger.debug("Writing %s to the filesystem", self._path)

            try:
                with open(self._path, self._open_option) as fout:
                    fout.write(self._image)
                    logger.debug("Wrote %s to the filesystem", self._path)

                return True
            except Exception as e:
                logger.error(
                    "Failed to write %s to the filesystem; %s", self._path, e)

        return False

    def revert(self) -> bool:
        """Deletes the artwork image from the filesystem.

        Returns:
            `True` if the image was deleted from the filesystem successfully; otherwise `False`.
        """
        logger.debug("Deleting %s from the filesystem", self._path)

        try:
            os.remove(self._path)
            return True
        except OSError as ose:
            logger.error(
                "Failed to delete %s from the filesystem; %s", self._path, ose)

        return False


class WriteMetadataCommand(Command):
    """Class for writing artwork metadata to the filesystem.

    The metadata is written to the `path` directory as bytes with the `.json` extension.

    Attributes:
        artwork (Artwork):
            Metadata describing the artistic work.
        path (str):
            Path to the output directory where the JSON metadata will be written.
        indent (int):
            Enable pretty-printing; number of spaces to indent.
        sort_keys (bool):
            Sort the JSON keys in alphabetical order.
        open_option (str):
            File mode to open the file for write access.
    """

    def __init__(
        self,
        dir_path: str,
        artwork: Artwork,
        indent: Optional[int],
        sort_keys: bool,
        overwrite_existing: bool,
    ) -> None:
        """Constructs a new `WriteMetadataCommand` instance."""
        self._artwork = artwork

        # Create a clean base filename by converting to a slug
        slug = slugify(f"{artwork.artist}-{artwork.title}")
        self._path = f"{dir_path}{os.path.sep}{slug}.json"

        self._indent = indent
        self._sort_keys = sort_keys

        self._open_option = "w" if overwrite_existing else "x"

    def execute(self) -> bool:
        """Writes this artwork metadata to the filesystem.

        Returns:
            `True` if the metadata was written to the filesystem successfully; otherwise `False`.
        """
        logger.debug("Writing %s to the filesystem", self._path)

        try:
            with open(self._path, self._open_option) as fout:
                artwork_dict = vars(self._artwork)
                artwork_dict.pop("image")

                json.dump(
                    artwork_dict,
                    fout,
                    indent=self._indent,
                    sort_keys=self._sort_keys,
                    ensure_ascii=False,
                )
                logger.debug("Wrote %s to the filesystem", self._path)

            return True
        except Exception as e:
            logger.error(
                "Failed to write %s to the filesystem; %s", self._path, e)

        return False

    def revert(self) -> bool:
        """Deletes this artwork metadata from the filesystem.

        Returns:
            `True` if the metadata was deleted from the filesystem successfully; otherwise `False`.
        """
        logger.debug("Deleting %s from the filesystem", self._path)

        try:
            os.remove(self._path)
            return True
        except OSError as ose:
            logger.error(
                "Failed to delete %s from the filesystem; %s", self._path, ose)

        return False
