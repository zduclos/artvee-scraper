# artvee-scraper
![PyPI Version](https://img.shields.io/pypi/v/artvee-scraper.svg)

**artvee-scraper** is an easy to use library for fetching public domain artwork from [Artvee](https://www.artvee.com).

- [Artvee Web-scraper](#artvee-scraper)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
  - [Examples](#examples)
  - [API Reference](#api-reference)

## Overview
Artvee-scraper is a web scraper which concurrently extracts artwork from Artvee. Callbacks are notified asynchronously for each scraped
artwork so that user-defined actions may be taken. These actions are typically used to store the artwork, which can subsequently be used
for display, machine learning, or other applications.

> If you are seeking a command line utility, please note that it has been relocated to a separate project - [artvee-scraper-cli](https://github.com/zduclos/artvee-scraper-cli). Alternatively, you may still use [artvee-scraper 3.0.1](https://pypi.org/project/artvee-scraper/3.0.1/).

## Installation

Using PyPI
```console
$ python -m pip install artvee-scraper
```
Python 3.10+ is officially supported.

## Getting Started
1. Create callbacks (lambda, function, method).
    ```python
    # Use a lambda to log the event
    log_event = lambda artwork, thrown: logger.info(
        "Processing '%s' by %s", artwork.title, artwork.artist
    )
    
    # Write the artwork to a file as JSON format
    def on_artwork_received(artwork: Artwork, thrown: Exception | None = None) -> None:
        if thrown is None:
            with open(f"/tmp/{artwork.resource}.json", "w", encoding="UTF-8") as fout:
                json.dump(artwork.to_dict(), fout, ensure_ascii=False)
    ```
2. Initialize the scraper.
    ```python
    scraper = ArtveeScraper() # scrapes all categories by default
    ```
3. Register callbacks. The callbacks will be notified asynchronously for each event in the order that they are registered.
    ```python
    scraper.register_listener(log_event).register_listener(on_artwork_received)
    ```
4. Start scraping. Use either the context manager construct, or join to block until done.<br>
    `Example 1 - using context manager`
    ```python
    with scraper as s:
        s.start() # blocks until done
    ```
    `Example 2 - using join()`
    ```python
    scraper.start()
      ... // do other things
    scraper.join() # blocks until done
    ```

## Examples
**Create** `app.py`
```python
import logging
import os

from artvee_scraper.artvee_client import CategoryType
from artvee_scraper.artwork import Artwork
from artvee_scraper.scraper import ArtveeScraper

# Set up logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s [%(threadName)s] %(module)s.%(funcName)s(%(lineno)d) | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


def handle_event(artwork: Artwork, thrown: Exception | None = None) -> None:
    """A callback for handling the result of an artwork processing event."""

    if thrown is not None:
        # An error occurred; the artwork is partially populated (missing artwork.image.raw)
        logger.error("Failed to process artist=%s, title=%s, url=%s; %s", artwork.artist, artwork.title, artwork.url, thrown)
    else:
        file_path = os.path.expanduser(f"~/Downloads/{artwork.resource}.jpg") # create a unique filename
        logger.info("Writing %s to %s", artwork.title, file_path)

        # Write the raw image bytes to a file. 
        with open(file_path, "wb") as fout:
            fout.write(artwork.image.raw)


def main():
    # Choose which categories to scrape. Using `list(CategoryType)` creates a list of all categories.
    categories = [CategoryType.ABSTRACT, CategoryType.DRAWINGS]

    # Initialize the scraper
    scraper = ArtveeScraper(categories=categories)

    # Register listener functions
    scraper.register_listener(handle_event)

    # Start scraping
    with scraper as s:
        s.start() # blocks until done


if __name__ == "__main__":
    main()
```

**Run** `app.py`
```shell
me@linux-desktop:~$ python app.py
2038-01-19 19:36:36.839 DEBUG [MainThread] scraper.start(125) | Starting
2038-01-19 19:36:36.839 DEBUG [Thread-1 (_exec)] scraper._exec(152) | Executing scraper for categories [<CategoryType.ABSTRACT: 'abstract'>, <CategoryType.DRAWINGS: 'drawings'>]
2038-01-19 19:36:36.839 DEBUG [Thread-1 (_exec)] artvee_client.get_page_count(113) | Retrieving page count; category=abstract
2038-01-19 19:36:36.854 DEBUG [Thread-1 (_exec)] connectionpool._new_conn(1051) | Starting new HTTPS connection (1): artvee.com:443
2038-01-19 19:36:37.737 DEBUG [Thread-1 (_exec)] connectionpool._make_request(546) | https://artvee.com:443 "GET /c/abstract/page/1/?per_page=70 HTTP/11" 301 0
2038-01-19 19:36:37.827 DEBUG [Thread-1 (_exec)] connectionpool._make_request(546) | https://artvee.com:443 "GET /c/abstract/?per_page=70 HTTP/11" 200 19573
2038-01-19 19:36:37.955 DEBUG [Thread-1 (_exec)] scraper._exec(160) | Category abstract has 108 page(s)
2038-01-19 19:36:37.955 DEBUG [Thread-1 (_exec)] scraper._exec(166) | Processing category abstract, page (1/108)
2038-01-19 19:36:37.955 DEBUG [Thread-1 (_exec)] artvee_client.get_metadata(152) | Retrieving metadata; category=abstract, page=1
    ...
```

## API Reference
API documentation is available on [Read the Docs](https://artvee-scraper.readthedocs.io/).