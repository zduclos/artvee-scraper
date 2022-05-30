import base64
from dataclasses import dataclass
from typing import Optional


@dataclass
class Artwork:
    """Represents an artistic work.

    Attributes:
        url (str):
            Image download URL
        title (str):
            Name of the artwork
        category (str):
            Category the work of art is depicting (ex: abstract, still-life, animals, etc)
        artist (str, optional):
            Name of the person that created this artwork. Defaults to `Unknown Artist`
        date (str, optional):
            Year or date range the artwork was completed (ex: 2012 - 2019). Defaults to `n.d.`, no date
        origin (str, optional):
            Artist nationality and lifespan (ex: Austrian, 1834-1921). Defaults to `None`
        image (bytes, optional):
            JPG formatted image bytes. Defaults to `None`
    """

    url: str
    title: str
    category: str
    artist: str = "Unknown Artist"
    date: str = "n.d."
    origin: Optional[str] = None
    image: Optional[bytes] = None

    def get_image_encoded(self) -> Optional[str]:
        """Returns the image encoded as Base64 binary.

        Returns:
            Base64 binary encoded image.
        """
        return (
            str(base64.b64encode(self.image).decode("utf-8"))
            if self.image is not None
            else None
        )

    def to_dict(self) -> dict:
        """A dict representation of this object.

        The image will be encoded in Base64 binary.

        Returns:
            This object as a dict.
        """
        d = self.__dict__
        d["image"] = self.get_image_encoded()
        return d
