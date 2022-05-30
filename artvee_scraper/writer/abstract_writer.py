from abc import ABC, abstractmethod

from artvee_scraper.artwork import Artwork


class AbstractWriter(ABC):
    @abstractmethod
    def write(self, artwork: Artwork) -> bool:
        raise NotImplementedError
