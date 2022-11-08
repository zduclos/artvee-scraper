import concurrent.futures
import logging
import math
import re
import traceback
from enum import Enum
from typing import List, Optional

import requests
from bs4 import BeautifulSoup, Tag

from artvee_scraper.writer.file_writer import AbstractWriter

from .artwork import Artwork

logger = logging.getLogger("artvee-scraper")


class CategoryType(Enum):
    ABSTRACT = "abstract"
    FIGURATIVE = "figurative"
    LANDSCAPE = "landscape"
    RELIGION = "religion"
    MYTHOLOGY = "mythology"
    POSTERS = "posters"
    ANIMALS = "animals"
    ILLUSTRATION = "illustration"
    STILL_LIFE = "still-life"
    BOTANICAL = "botanical"
    DRAWINGS = "drawings"
    ASIAN_ART = "asian-art"

    def __str__(self):
        return self.value

    def __lt__(self, other):
        return self.value < other.value


class ImageSize(Enum):
    MAX = "https://mdl.artvee.com/hdl/"
    STANDARD = "https://mdl.artvee.com/sdl/"


class ArtveeScraper:
    _ITEMS_PER_PAGE = 70
    _PATTERN = re.compile("^(.+) *\\((.+)\\) *$")

    def __init__(
        self,
        writer: AbstractWriter,
        worker_threads: int = 3,
        categories: List[CategoryType] = list(CategoryType),
        image_size: ImageSize = ImageSize.STANDARD,
    ) -> None:
        self.writer = writer
        self.workers = concurrent.futures.ThreadPoolExecutor(
            max_workers=worker_threads)
        self.categories = categories
        self.image_size = image_size

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.shutdown(True)

    def start(self):
        logger.info("Starting scraper for categories %s", self.categories)

        for category in self.categories:
            page_count = ArtveeScraper._num_pages_for_category(category)

            logger.info("Category %s has %d page(s)", category, page_count)
            for page in range(1, page_count + 1):
                logger.info("Processing %s (%d/%d)",
                            category, page, page_count)
                page_url = f"https://www.artvee.com/c/{category}/page/{page}/?per_page={ArtveeScraper._ITEMS_PER_PAGE}"
                artwork_list = ArtveeScraper._scrape_artwork_data(
                    page_url, category.value.capitalize())

                results = self.workers.map(self._worker_task, artwork_list)

                # Block until all submitted tasks for a page have completed
                for r in results:
                    pass

    def shutdown(self, wait: bool) -> None:
        self.workers.shutdown(wait=wait)

    def _worker_task(self, artwork: Artwork) -> bool:
        logger.info("Processing artwork %s", artwork)

        try:
            if img_link := self._image_link_from(artwork.url):
                # Download image
                img_resp = requests.get(img_link)

                if img_resp.status_code == 200:
                    # Write the artwork to destination
                    artwork.image = img_resp.content  # raw image bytes
                    return self.writer.write(artwork)

                logger.error(
                    "Failed to download artwork from URL %s; Status Code: %d",
                    img_link,
                    img_resp.status_code,
                )
            logger.error(
                "Failed to extract image link from URL %s", artwork.url)
        except Exception:
            logging.error(
                "An error occured while processing %s; %s",
                artwork,
                traceback.format_exc(),
            )

        return False

    def _image_link_from(self, artwork_url: str) -> Optional[str]:
        logger.debug("Retrieving image download link from URL %s", artwork_url)
        download_page_resp = requests.get(artwork_url)

        if download_page_resp.status_code == 200:
            soup = BeautifulSoup(download_page_resp.content, "html.parser")
            img_links = soup.find_all(
                "a",
                {
                    "class": "prem-link gr btn dis snax-action snax-action-add-to-collection snax-action-add-to-collection-downloads"
                },
            )

            # Select the correct max/standard image size link
            for link in img_links:
                link_dest = link.get("href")
                if link_dest.startswith(self.image_size.value):
                    return link_dest

            logger.error("Download link for %s image size is not available",
                         self.image_size.name)
        else:
            logger.error(
                "Failed to retrieve image download link from URL %s; Status Code: %d",
                artwork_url,
                download_page_resp.status_code,
            )

        return None

    @staticmethod
    def _num_pages_for_category(category: CategoryType) -> int:
        logger.debug(
            "Calculating the number of pages required by category '%s'", category
        )
        url = f"https://artvee.com/c/{category}/page/1/?per_page={ArtveeScraper._ITEMS_PER_PAGE}"

        try:
            resp = requests.get(url)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "html.parser")

                total_items = (
                    soup.find("p", class_="woocommerce-result-count")
                    .text.strip("items")
                    .strip()
                )

                return math.ceil(int(total_items) / ArtveeScraper._ITEMS_PER_PAGE)

            logger.error(
                "Failed to retrieve total number of items from URL %s; Status Code: %d",
                url,
                resp.status_code,
            )
        except Exception:
            logging.error(
                "An error occured while retrieving total number of items from %s; %s",
                url,
                traceback.format_exc(),
            )

        return 0

    @staticmethod
    def _scrape_artwork_data(page_url: str, category: str) -> List[Artwork]:
        scraped_artwork = []

        try:
            logger.debug("Retrieving artwork metadata URL %s", page_url)
            website_resp = requests.get(page_url)

            if website_resp.status_code == 200:
                soup = BeautifulSoup(
                    website_resp.content.decode("utf-8"), "html.parser"
                )
                all_metadata_html = soup.find_all(
                    "div", {"class": "product-element-bottom"}
                )

                for meta in all_metadata_html:
                    if artwork := ArtveeScraper._parse_metadata_html(meta, category):
                        scraped_artwork.append(artwork)

            else:
                logger.error(
                    "Failed to retrieve website from URL %s; Status Code: %d",
                    page_url,
                    website_resp.status_code,
                )
        except Exception:
            logging.error(
                "An error occured while processing %s; %s",
                page_url,
                traceback.format_exc(),
            )

        return scraped_artwork

    @staticmethod
    def _parse_metadata_html(metadata_html: Tag, category: str) -> Optional[Artwork]:
        try:
            img_details = metadata_html.find("h3", {"class": "product-title"})
            url = img_details.a.get("href")
            title = img_details.get_text(strip=True)

            artwork = Artwork(url, title, category)

            if title_matcher := ArtveeScraper._PATTERN.match(title):
                artwork.title = title_matcher.group(1).strip()
                artwork.date = title_matcher.group(2).strip()

            artist = metadata_html.find(
                "div", {"class": "woodmart-product-brands-links"}
            ).get_text(strip=True)

            if artist_matcher := ArtveeScraper._PATTERN.match(artist):
                artwork.artist = artist_matcher.group(1).strip()
                artwork.origin = artist_matcher.group(2).strip()
            else:
                artwork.artist = artist

            return artwork
        except Exception:
            logger.error(
                "Failed to parse content into a valid representation; %s",
                traceback.format_exc(),
            )

        return None
