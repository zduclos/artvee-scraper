import concurrent.futures
import logging
import traceback
from threading import Event, Lock, Thread
from typing import Callable, Tuple

from typing_extensions import Self

from .artvee_client import ArtveeClient
from .artwork import Artwork, ArtworkMetadata, CategoryType, Image, ImageMetadata

logger = logging.getLogger(__name__)


class ArtveeScraper:
    """A web scraper which concurrently extracts artwork from Artvee. Callbacks are notified asynchronously for
    each scraped artwork so that user-defined actions may be taken.

    Attributes:
        _artvee_client (ArtveeClient):
            An HTTP client for accessing artwork.
        _worker_pool (ThreadPoolExecutor):
            A pool of threads to manage concurrent scraping tasks.
        _categories (Tuple[CategoryType]):
            Category types to scrape.
        _boss_thread (Thread):
            The main thread responsible for executing the scraping logic; delegates tasks to workers.
        _stop_event (Event):
            Signal to indicate the scraping process should be halted.
        _listener_lock (Lock):
            A lock which provides access the listeners in a thread-safe manner.
        _listeners (dict):
            A hashset of callbacks to invoke asynchronously.

    Args:
        artvee_client (ArtveeClient, optional):
            An HTTP client for accessing artwork. Defaults to a new instance.
        worker_threads (int, optional):
            The number of worker threads to use for processing. Must be between 1 and 10. Defaults to 3.
        categories (Tuple[CategoryType], optional):
            Category types to scrape. Defaults to all categories.

    Raises:
        ValueError:
            If `worker_threads` is not in the range [1, 10].
    """

    def __init__(
        self,
        artvee_client: ArtveeClient = ArtveeClient(),
        worker_threads: int = 3,
        categories: Tuple[CategoryType] = tuple(CategoryType),
    ) -> None:
        """Initializes a newly created `ArtveeScraper` object."""

        self._artvee_client = artvee_client
        if not 1 <= worker_threads <= 10:
            raise ValueError("Worker threads must be in range [1-10]")
        self._worker_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=worker_threads
        )
        self._categories = categories

        self._boss_thread = Thread(target=self._exec, args=())
        self._stop_event = Event()
        self._listener_lock = Lock()
        self._listeners = {}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.join()

    def register_listener(
        self,
        on_event_listener: Callable[[Artwork, Exception | None], None],
    ) -> Self:
        """Registers a callback to be notified of events asynchronously.

        A callback may only be registered once; additional attempts to register the same callback will
        overwrite the previous registration. The `success` notification contains a fully populated `Artwork`,
        whereas the `failure` notification contains a partially populated `Artwork` and associated exception.

        Args:
            on_event_listener (Callable[[Artwork, Exception | None], None]):
                A callback function that will be notified async when an event occurs.

        Raises:
            ValueError:
                If the provided `on_event_listener` argument is not callable.

        Returns:
            `self` for method chaining
        """

        if not callable(on_event_listener):
            raise ValueError("On event listener callback must be a callable type")

        with self._listener_lock:
            tmp = self._listeners.copy()
            tmp[on_event_listener] = None  # dict as a hashset
            self._listeners = tmp
            return self

    def deregister_listener(
        self,
        on_event_listener: Callable[[Artwork, Exception | None], None],
    ) -> Self:
        """Deregisters a callback so that it will no longer be notified of events.

        Args:
            on_event_listener (Callable[[Artwork, Exception | None]], None]):
                The callback to no longer notify when an event occurs.

        Returns:
            `self` for method chaining
        """

        with self._listener_lock:
            tmp = self._listeners.copy()
            tmp.pop(on_event_listener, None)
            self._listeners = tmp
            return self

    def start(self) -> None:
        """Begin scraping artwork

        Returns:
            None
        """

        logger.debug("Starting")
        self._boss_thread.start()

    def join(self) -> None:
        """Blocks the calling thread until all active tasks have been completed.

        Returns:
            None
        """

        logger.debug("Waiting for all active tasks to complete")
        self._boss_thread.join()
        self._worker_pool.shutdown(wait=True, cancel_futures=False)

    def shutdown(self) -> None:
        """Initiates a shutdown in which running tasks are completed, but all pending tasks are canceled.

        Returns:
            None
        """

        logger.debug("Shutting down")
        self._stop_event.set()
        self._boss_thread.join()
        self._worker_pool.shutdown(wait=True, cancel_futures=True)

    def _exec(self) -> None:
        logger.debug("Executing scraper for categories %s", self._categories)

        for category in self._categories:
            if self._stop_event.is_set():
                return

            try:
                page_count = self._artvee_client.get_page_count(category)
                logger.debug("Category %s has %d page(s)", category, page_count)

                for page in range(1, page_count + 1):
                    if self._stop_event.is_set():
                        return

                    logger.debug(
                        "Processing category %s, page (%d/%d)",
                        category,
                        page,
                        page_count,
                    )

                    try:
                        # Scrape the page's metadata
                        metadata_tuples = self._artvee_client.get_metadata(
                            category, page
                        )

                        # Submit tasks to download the images; invoke the listeners for each
                        results = self._worker_pool.map(
                            self._worker_task, metadata_tuples
                        )

                        # Block until all submitted tasks for a page have completed
                        for _ in results:
                            pass
                    except Exception:
                        logging.warning(
                            "An error occured while processing page %d of category %s; %s",
                            page,
                            category,
                            traceback.format_exc(),
                        )
            except Exception:
                logging.error(
                    "An error occured while processing category %s; %s",
                    category,
                    traceback.format_exc(),
                )

    def _worker_task(
        self, metadata_tuple: Tuple[ArtworkMetadata, ImageMetadata]
    ) -> None:
        """Artwork processing task.

        Retrieves the image, coalescing it with the metadata into an `Artwork` object.
        If the image bytes are successfully retrieved, any registered listeners will be invoked with a fully populated `Artwork`.
        If an exception is encountered while retrieving the image, any registered listeners will be invoked with a partially
        populated `Artwork` along with the exception that was thrown.

        Args:
            metadata_tuple (Tuple[ArtworkMetadata, ImageMetadata]):
                A pair of related metadata which provides the attributes of an artwork.
                - `ArtworkMetadata`: Attributes of an artwork.
                - `ImageMetadata`: Attributes of an image file.

        Returns:
            None
        """

        artwork_metadata, img_metadata = metadata_tuple

        # Unpack the metadata to partially populate the artwork
        artwork = Artwork(**vars(artwork_metadata))
        artwork.image = Image(**vars(img_metadata))

        try:
            artwork.image.raw = self._artvee_client.get_image(img_metadata)

            self._invoke_listeners(artwork)  # artwork is fully populated
        except Exception as thrown:
            self._invoke_listeners(
                artwork, thrown
            )  # artwork is partially populated (missing raw image)

    def _invoke_listeners(
        self, artwork: Artwork, thrown: Exception | None = None
    ) -> None:
        """Invokes registered callback functions.

        Args:
            artwork (Artwork): The artwork. Partially populated if an exception has occurred.
            thrown (Exception, optional): The processing exception. Defaults to None.

        Returns:
            None
        """
        for listener in self._listeners.keys():
            listener(artwork, thrown)
