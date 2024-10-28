import pytest
from mockito import ANY, mock, unstub, verify, when

from artvee_scraper.artvee_client import ArtveeClient
from artvee_scraper.artwork import ArtworkMetadata, CategoryType, ImageMetadata
from artvee_scraper.scraper import ArtveeScraper


@pytest.fixture(autouse=True)
def cleanup():
    unstub()


def test_artvee_scraper():

    artvee_client_mock = mock(ArtveeClient)

    # Mock ArtveeClient::get_page_count
    when(artvee_client_mock).get_page_count(ANY(CategoryType)).thenReturn(1)

    # Mock ArtveeClient::get_metadata
    artwork_metadata = ArtworkMetadata(
        "https://artvee.com/dl/prismes-4/",
        "prismes-4",
        "Prismes-4",
        "Abstract",
        "Emile-Allain Séguy",
        "1931",
        "French, 1877-1951",
    )
    img_metadata = ImageMetadata(
        "https://mdl.artvee.com/sdl/101108absdl.jpg", 1283, 1800, 2.4, "MB"
    )

    when(artvee_client_mock).get_metadata(ANY(CategoryType), ANY(int)).thenReturn(
        [(artwork_metadata, img_metadata)]
    )

    # Mock ArtveeClient::get_image
    img = "dGVzdF9nZXRfaW1hZ2U=".encode("ascii")
    when(artvee_client_mock).get_image(ANY(ImageMetadata)).thenReturn(img)

    # Setup
    captured_artwork = None

    def captor_fn(artwork, thrown):
        nonlocal captured_artwork
        captured_artwork = artwork

    # Test
    artvee_scraper = ArtveeScraper(
        artvee_client=artvee_client_mock,
        categories=(CategoryType.ABSTRACT,),
        worker_threads=1,
    ).register_listener(captor_fn)

    artvee_scraper.start()
    artvee_scraper.join()

    # Validate
    assert "https://artvee.com/dl/prismes-4/" == captured_artwork.url, "url is invalid"
    assert "prismes-4" == captured_artwork.resource, "resource is invalid"
    assert "Prismes-4" == captured_artwork.title, "title is invalid"
    assert "Abstract" == captured_artwork.category, "category is invalid"
    assert "Emile-Allain Séguy" == captured_artwork.artist, "artist is invalid"
    assert "1931" == captured_artwork.date, "date is invalid"
    assert "French, 1877-1951" == captured_artwork.origin, "origin is invalid"
    assert (
        "https://mdl.artvee.com/sdl/101108absdl.jpg"
        == captured_artwork.image.source_url
    ), "image url is invalid"
    assert 1283 == captured_artwork.image.width, "image width is invalid"
    assert 1800 == captured_artwork.image.height, "image height is invalid"
    assert 2.4 == captured_artwork.image.file_size, "file_size is invalid"
    assert "MB" == captured_artwork.image.file_size_unit, "file_size_unit is invalid"
    assert img == captured_artwork.image.raw, "image is invalid"
    assert "jpg" == captured_artwork.image.format_name, "format name is invalid"

    verify(artvee_client_mock, times=1).get_page_count(CategoryType.ABSTRACT)
    verify(artvee_client_mock, times=1).get_metadata(CategoryType.ABSTRACT, 1)
    verify(artvee_client_mock, times=1).get_image(img_metadata)
