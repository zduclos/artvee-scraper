import json
import logging
from dataclasses import dataclass

from artvee_scraper.artwork import Artwork

from .abstract_writer import AbstractWriter

logger = logging.getLogger(f"artvee-scraper.{__name__}")


class JsonConsoleWriter(AbstractWriter):
    """Class for writing an artwork to the console as a JSON object.

    Attributes:
        space_level (int, optional):
            Enable pretty-printing; number of spaces to indent. Defaults to `0`.
        sort_keys (bool, optional):
            Sort the JSON keys in alphabetical order. Defaults to `False`.
        include_image (bool, optional):
            If `True`, the Base64 binary encoded image will be included in the output. Defaults to `False`.
    """

    def __init__(
        self, space_level: int = 0, sort_keys: bool = False, include_image: bool = False
    ) -> None:
        self._indent = space_level if space_level > 1 else None
        self._sort_keys = sort_keys
        self._include_image = include_image

    def write(self, artwork: Artwork) -> bool:
        """Writes the artwork to the console as a JSON object.

        Args:
            artwork:
                Artistic work to be written to the console.

        Returns:
            `True` if the artwork was written to the console successfully; otherwise `False`.
        """
        if not self._include_image:
            artwork.image = None

        logger.info(
            json.dumps(
                artwork.to_dict(),
                indent=self._indent,
                sort_keys=self._sort_keys,
                ensure_ascii=False,
            )
        )

        return True
