from __future__ import annotations

import base64
from dataclasses import dataclass
from enum import Enum


@dataclass
class ArtworkMetadata:
    """Information that describes attributes of an artwork.

    Attributes:
        url (str):
            Artwork URL (ex: https://artvee.com/dl/zwei-tanzende/)
        resource (str):
            Unique name of artwork; extracted from the URL (ex: zwei-tanzende)
        title (str):
            Name of the artwork (ex: Zwei Tanzende)
        category (str):
            Category the work of art is depicting (ex: abstract)
        artist (str, optional):
            Name of the person that created this artwork. Defaults to `Unknown Artist`
        date (str, optional):
            Year or date range the artwork was completed (ex: 2012 - 2019). Defaults to `n.d.`, no date
        origin (str, optional):
            Artist nationality and lifespan (ex: Austrian, 1834-1921). Defaults to `None`
    """

    url: str
    resource: str
    title: str
    category: str
    artist: str = "Unknown Artist"
    date: str = "n.d."
    origin: str | None = None


@dataclass
class Artwork(ArtworkMetadata):
    """Represents an artistic work.

    Attributes:
        image (Image, optional):
            The image, including associated metadata. Defaults to `None`
    """

    image: Image | None = None

    def to_dict(self) -> dict | None:
        """A dict representation of this object.

        The image will be encoded in Base64 binary.

        Returns:
            This object as a dict.
        """
        return dict(self.__dict__, image=self.image.to_dict() if self.image else None)


@dataclass
class ImageMetadata:
    """Information that describes attributes of an image file.

    Attributes:
        source_url (str, optional):
            The URL where the image is sourced from. Defaults to `None`
        width (int, optional):
            The width of the image in pixels. Defaults to `0`
        height (int, optional):
            The height of the image in pixels. Defaults to `0`
        file_size (float, optional):
            The size of the image file. Defaults to `0`
        file_size_unit (str, optional):
            The unit of the file size (ex: "KB", "MB"). Defaults to `None`
    """

    source_url: str | None = None
    width: int = 0
    height: int = 0
    file_size: float = 0
    file_size_unit: str | None = None


@dataclass
class Image(ImageMetadata):
    """Represents a graphical image.

    Attributes:
        raw (bytes, optional):
            The raw binary data of the image. Defaults to `None`
        format_name (str, optional):
            The format of the image file - identifies how the image should be processed/displayed. Defaults to `jpg`.
    """

    raw: bytes | None = None
    format_name: str = "jpg"

    def b64encoded(self) -> str | None:
        """Returns the image encoded as Base64 binary.

        Returns:
            Base64 binary encoded image.
        """
        return (
            str(base64.b64encode(self.raw).decode("utf-8"))
            if self.raw is not None
            else None
        )

    def to_dict(self) -> dict | None:
        """A dict representation of this object.

        The image will be encoded in Base64 binary.

        Returns:
            This object as a dict.
        """
        return dict(self.__dict__, raw=self.b64encoded())


class CategoryType(Enum):
    """Enumeration for different categories of art.

    Attributes:
        ABSTRACT (str):
            Art that uses shapes, colors, forms, and gestural marks rather than aiming for an accurate representation
            of visual reality.
        FIGURATIVE (str):
            Art that represents recognizable subjects, particularly the human figure, focusing on real-world forms.
        LANDSCAPE (str):
            Art that depicts natural scenes, often focusing on the beauty and atmosphere of the environment.
        RELIGION (str):
            Art that conveys spiritual themes or depicts subjects related to faith, spirituality, and religious practices.
        MYTHOLOGY (str):
            Art that illustrates or interprets themes, characters, and stories from myths and legends, often exploring
            cultural beliefs and narratives.
        POSTERS (str):
            Art designed for display and promotion, often featuring bold imagery and text to convey a message or advertise
            events, products, or causes.
        ANIMALS (str):
            Art that focuses on the representation of animals, capturing their form, behavior, and characteristics.
        ILLUSTRATION (str):
            Art that creates images to accompany text or convey a narrative, often found in books, magazines, and advertising.
        STILL_LIFE (str):
            Art that depicts inanimate objects, such as fruits, flowers, and everyday items.
        BOTANICAL (str):
            Art that focuses on the representation of plants and flowers, often emphasizing accuracy and detail to depict
            their beauty and scientific characteristics.
        DRAWINGS (str):
            Art form created using various mediums, such as pencil, charcoal, or ink, to render images through lines and
            shading, often capturing ideas, sketches, or detailed representations.
        ASIAN_ART (str):
            Art that represents styles and techniques from Asian cultures, often reflecting traditional themes, motifs,
            and cultural significance.
    """

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
