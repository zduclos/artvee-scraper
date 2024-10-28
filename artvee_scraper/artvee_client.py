import json
import logging
import math
import re
import traceback
from typing import Final, List, Tuple
from urllib.parse import unquote_plus

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .artwork import ArtworkMetadata, CategoryType, ImageMetadata

logger = logging.getLogger(__name__)


class ArtveeClient:
    """HTTP client for interacting with the Artvee API.

    Constants:
        _HTTP_CONN_TIMEOUT_SEC (float):
            Default number of seconds to wait to establish a connection to a remote machine.
        _HTTP_READ_TIMEOUT_SEC (float):
            Default number of seconds the client will wait for the server to send a response.
        _ITEMS_PER_PAGE (int):
            Maximum number of items to retrieve per page in API requests.
        _TITLE_PATTERN (re.Pattern):
            Regex pattern for extracting title and date. ex: `Landscape with Weather Vane (1935)`;
            group 1 = title (ex: Landscape with Weather Vane), group 2 = date (ex: 1935)
        _ARTIST_PATTERN (re.Pattern):
            Regex pattern for extracting artist name and origin. ex: `Arthur Dove(American, 1880-1946)`;
            group 1 = artist name (ex: Arthur Dove), group 2 = origin (ex: American, 1880-1946)
        _RESOURCE_PATTERN (re.Pattern):
            Regex pattern for extracting the resource name. ex: `https://artvee.com/dl/zwei-tanzende/`;
            group 1 = resource (ex: zwei-tanzende)
        _IMG_DIMENSION_PATTERN (re.Pattern):
            Regex pattern for extracting image dimensions. ex: `1800 x 1185px`;
            group 1 = width (ex: 1800), group 2 = height (ex: 1185)
        _IMG_FILE_SIZE_PATTERN (re.Pattern):
            Regex pattern for extracting image file size and unit.ex: `1.82 MB`; group 1 = size (ex: 1.82), group 2 = unit (ex: MB)

    Attributes:
        _timeout (tuple[float, float]):
            Timeouts to use for HTTP requests.
        _session (Session):
            Allows persistance of parameters across HTTP requests.

    Args:
        conn_timeout (float, optional):
            Number of seconds to wait to establish a connection to a remote machine. Defaults 3.05 seconds.
        read_timeout (float, optional):
            Number of seconds the client will wait for the server to send a response. Defaults to 10 seconds.
        max_attempts (int, optional):
            The maximum number of attempts (including the initial call). Must be between 1 and 10.
            Defaults to 3 (initial call + two retries).

    Raises:
        ValueError:
            If `conn_timeout` is not positive.
            If `read_timeout` is not positive.
            If `max_attempts` is not in the range [1, 10].
    """

    _HTTP_CONN_TIMEOUT_SEC: Final[float] = 3.05
    _HTTP_READ_TIMEOUT_SEC: Final[float] = 10

    _ITEMS_PER_PAGE: Final[int] = 70

    _TITLE_PATTERN: Final[re.Pattern] = re.compile("^(.+) *\\((.+)\\) *$")
    _ARTIST_PATTERN: Final[re.Pattern] = re.compile("^(.+) *\\((.+)\\) *$")
    _RESOURCE_PATTERN: Final[re.Pattern] = re.compile(
        "^https://artvee\\.com/dl/((\\w|-|%)+)/$"
    )
    _IMG_DIMENSION_PATTERN: Final[re.Pattern] = re.compile("^(\\d+)\\sx\\s(\\d+)px$")
    _IMG_FILE_SIZE_PATTERN: Final[re.Pattern] = re.compile(
        "^((?:[0-9]*\\.)?[0-9]+)\\s([A-Za-z]+)$"
    )

    def __init__(
        self,
        conn_timeout: float = _HTTP_CONN_TIMEOUT_SEC,
        read_timeout: float = _HTTP_READ_TIMEOUT_SEC,
        max_attempts: int = 3,
    ) -> None:
        """Initializes a newly created `ArtveeClient` object."""

        if conn_timeout < 0:
            raise ValueError("Connection timeout cannot be a negative number")
        if read_timeout < 0:
            raise ValueError("Read timeout cannot be a negative number")
        self._timeout = (conn_timeout, read_timeout)

        if not 1 <= max_attempts <= 10:
            raise ValueError("Max attempts must be in range [1-10]")

        retry_config = Retry(
            total=max_attempts - 1,  # number of retry attempts
            backoff_factor=1,  # seconds
            backoff_jitter=True,
            status_forcelist=[502, 503, 504],  # transient failures
        )
        self._session = ArtveeClient._new_session(retry_config)

    def get_page_count(self, category: CategoryType) -> int:
        """Retrieve the total number of webpages for a given category.

        Args:
            category (CategoryType):
                The category for which to retrieve the page count.

        Returns:
            int: The total number of pages available for the specified category.

        Raises:
            requests.exceptions.HTTPError:
                If the HTTP request returns an unsuccessful status code.
            ValueError:
                If the total items cannot be parsed / converted to an integer.
        """

        logger.debug("Retrieving page count; category=%s", category)
        url = f"https://artvee.com/c/{category}/page/1/?per_page={self._ITEMS_PER_PAGE}"

        resp = self._session.get(
            url,
            timeout=self._timeout,
        )

        resp.raise_for_status()

        soup = BeautifulSoup(resp.content, "html.parser")

        total_items = (
            soup.find("p", class_="woocommerce-result-count")
            .text.strip("items")
            .strip()
        )

        return math.ceil(int(total_items) / self._ITEMS_PER_PAGE)

    def get_metadata(
        self, category: CategoryType, page: int
    ) -> List[Tuple[ArtworkMetadata, ImageMetadata]]:
        """Retrieve artwork metadata for a specified category and page.

        Args:
            category (CategoryType):
                The category for which to retrieve artwork metadata.
            page (int):
                The page number to retrieve the metadata from. Pages are indexed starting at 1.

        Returns:
            List[Tuple[ArtworkMetadata, ImageMetadata]]:
                A list where each tuple represents the attributes of an artwork.
                `ArtworkMetadata`: Attributes of an artwork.
                `ImageMetadata`: Attributes of an image file.

        Raises:
            requests.exceptions.HTTPError:
                If the HTTP request returns an unsuccessful status code.
        """

        logger.debug("Retrieving metadata; category=%s, page=%d", category, page)
        page_url = f"https://www.artvee.com/c/{category}/page/{page}/?orderby=title_asc&per_page={self._ITEMS_PER_PAGE}"

        resp = self._session.get(
            page_url,
            timeout=self._timeout,
        )

        resp.raise_for_status()

        soup = BeautifulSoup(resp.content.decode("utf-8"), "html.parser")
        all_metadata_html = soup.find_all("div", {"class": "product-element-bottom"})

        metadata_tuples = []
        for metadata_html in all_metadata_html:
            try:
                artwork_metadata = ArtveeClient._parse_artist_metadata(
                    metadata_html, category
                )
                image_metadata = ArtveeClient._parse_image_metadata(metadata_html)

                metadata_tuples.append((artwork_metadata, image_metadata))
            except Exception:
                logger.warning(traceback.format_exc())
                pass

        return metadata_tuples

    def get_image(self, img_metadata: ImageMetadata) -> bytes:
        """Retrieve the image data.

        Args:
            img_metadata (ImageMetadata):
                Information that describes attributes of an artwork.

        Returns:
            bytes:
                The raw JPG image data.

        Raises:
            requests.exceptions.HTTPError:
                If the HTTP request returns an unsuccessful status code.
        """

        logger.debug("Retrieving image; url=%s", img_metadata.source_url)
        get_img_resp = self._session.get(
            img_metadata.source_url,
            timeout=self._timeout,
        )

        get_img_resp.raise_for_status()
        return get_img_resp.content

    @staticmethod
    def _new_session(retry_config: Retry) -> requests.Session:
        session = requests.Session()

        adapter = HTTPAdapter(max_retries=retry_config)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @staticmethod
    def _parse_artist_metadata(
        metadata_html: Tag, category: CategoryType
    ) -> ArtworkMetadata:
        artist_details = metadata_html.find("h3", {"class": "product-title"})
        title = artist_details.get_text(strip=True)
        url = artist_details.a.get("href")
        resource = ArtveeClient._RESOURCE_PATTERN.match(url).group(1)
        resource = unquote_plus(resource)

        artwork_metadata = ArtworkMetadata(
            url, resource, title, category.value.capitalize()
        )

        if title_matcher := ArtveeClient._TITLE_PATTERN.match(title):
            artwork_metadata.title = title_matcher.group(1).strip()
            artwork_metadata.date = title_matcher.group(2).strip()

        artwork_metadata.artist = metadata_html.find(
            "div", {"class": "woodmart-product-brands-links"}
        ).get_text(strip=True)

        if artist_matcher := ArtveeClient._ARTIST_PATTERN.match(
            artwork_metadata.artist
        ):
            artwork_metadata.artist = artist_matcher.group(1).strip()
            artwork_metadata.origin = artist_matcher.group(2).strip()

        return artwork_metadata

    @staticmethod
    def _parse_image_metadata(metadata_html: Tag) -> ImageMetadata:
        img_details_json = metadata_html.find("div", {"class": "tbmc linko"}).get(
            "data-sk"
        )
        img_details = json.loads(img_details_json)

        img_metadata = ImageMetadata()

        sdl_image_size = img_details.get("sdlimagesize")
        if sdl_dimension_matcher := ArtveeClient._IMG_DIMENSION_PATTERN.match(
            sdl_image_size
        ):
            img_metadata.width = int(sdl_dimension_matcher.group(1))
            img_metadata.height = int(sdl_dimension_matcher.group(2))

        sdl_file_size = img_details.get("sdlfilesize")
        if sdl_file_size_matcher := ArtveeClient._IMG_FILE_SIZE_PATTERN.match(
            sdl_file_size
        ):
            img_metadata.file_size = float(sdl_file_size_matcher.group(1))
            img_metadata.file_size_unit = sdl_file_size_matcher.group(2)

        if sk := img_details.get("sk"):
            img_metadata.source_url = f"https://mdl.artvee.com/sdl/{sk}sdl.jpg"

        return img_metadata
