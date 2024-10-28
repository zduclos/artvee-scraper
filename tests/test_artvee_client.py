import textwrap

import pytest
import requests
from mockito import ANY, mock, unstub, verify, when

from artvee_scraper.artvee_client import ArtveeClient
from artvee_scraper.artwork import CategoryType, ImageMetadata


@pytest.fixture(autouse=True)
def cleanup():
    unstub()


def test_get_page_count():
    # Mock Response
    body = """\
        <!DOCTYPE html>
        <html lang="en-US">
            <body>
                <div class="f-btn">
                    <p class="woocommerce-result-count">7559 items</p>
                </div>           
            </body>
        </html>\
        """
    mock_response = mock(requests.Response)
    mock_response.content = textwrap.dedent(body)

    # Mock Session::get
    mock_session = mock(requests.Session)
    when(mock_session).get(
        "https://artvee.com/c/abstract/page/1/?per_page=70", timeout=(3.05, 10)
    ).thenReturn(mock_response)

    # Mock Response::raise_for_status
    when(mock_response).raise_for_status().thenReturn(None)

    # Setup
    client = ArtveeClient()
    client._session = mock_session

    # Test
    result = client.get_page_count(CategoryType.ABSTRACT)

    # Validate
    assert 108 == result, "page count is invalid"
    verify(mock_session, times=1).get(...)
    verify(mock_response, times=1).raise_for_status()


def test_get_page_count_raise_for_status():
    # Mock Response
    mock_response = mock(requests.Response)

    # Mock Session::get
    mock_session = mock(requests.Session)
    when(mock_session).get(ANY(str), ...).thenReturn(mock_response)

    # Mock Response::raise_for_status
    when(mock_response).raise_for_status().thenRaise(
        requests.ReadTimeout("Read timed out. (read timeout=0.05)")
    )

    # Setup
    client = ArtveeClient()
    client._session = mock_session

    # Test
    with pytest.raises(requests.Timeout):
        client.get_page_count(CategoryType.ABSTRACT)

    verify(mock_session, times=1).get(...)
    verify(mock_response, times=1).raise_for_status()


def test_get_metadata():
    # Mock Response
    body = """\
        <!DOCTYPE html>
        <html lang="en-US">
            <body>
                <div class="product-element-bottom mmbb-m">
                    <div class="pbm">
                        <div class="tbmc linko" data-cnt="10" data-id="220299" data-sk='{"sdlimagesize":"1269 x 1800px","hdlimagesize":"3157 x 4478px","hdlfilesize":"15.65 MB","sdlfilesize":"2.63 MB","sk":"105247ab"}' data-url="/dl/man-playing-the-guitar" data-yr="1">
                            <h3 class="product-title"><a href="https://artvee.com/dl/man-playing-the-guitar/">Man playing the guitar (1924) </a></h3>
                        </div>
                        <div class="woodmart-product-brands-links" data-aid="6669" data-df=""><a href="https://artvee.com/artist/eugeniusz-zak/">Eugeniusz Zak</a> (Polish, 1884-1926)</div>
                    </div>
                </div>
            </body>
        </html>\
        """
    mock_response = mock(requests.Response)
    mock_response.content = textwrap.dedent(body).encode("utf-8")

    # Mock Session::get
    mock_session = mock(requests.Session)
    when(mock_session).get(
        "https://www.artvee.com/c/abstract/page/5/?orderby=title_asc&per_page=70",
        timeout=(3.05, 10),
    ).thenReturn(mock_response)

    # Mock Response::raise_for_status
    when(mock_response).raise_for_status().thenReturn(None)

    # Setup
    client = ArtveeClient()
    client._session = mock_session

    # Test
    result = client.get_metadata(CategoryType.ABSTRACT, 5)

    # Validate
    assert 1 == len(
        result
    ), "get_metadata() response contains an invalid number of items"

    artwork_metadata, img_metadata = result[0]
    assert (
        "https://artvee.com/dl/man-playing-the-guitar/" == artwork_metadata.url
    ), "url is invalid"
    assert "man-playing-the-guitar" == artwork_metadata.resource, "resource is invalid"
    assert "Man playing the guitar" == artwork_metadata.title, "title is invalid"
    assert "Abstract" == artwork_metadata.category, "category is invalid"
    assert "Eugeniusz Zak" == artwork_metadata.artist, "artist is invalid"
    assert "1924" == artwork_metadata.date, "date is invalid"
    assert "Polish, 1884-1926" == artwork_metadata.origin, "origin is invalid"
    assert (
        "https://mdl.artvee.com/sdl/105247absdl.jpg" == img_metadata.source_url
    ), "image url is invalid"
    assert 1269 == img_metadata.width, "image width is invalid"
    assert 1800 == img_metadata.height, "image height is invalid"
    assert 2.63 == img_metadata.file_size, "file_size is invalid"
    assert "MB" == img_metadata.file_size_unit, "file_size_unit is invalid"

    verify(mock_session, times=1).get(...)
    verify(mock_response, times=1).raise_for_status()


def test_get_metadata_raise_for_status():
    # Mock Response
    mock_response = mock(requests.Response)

    # Mock Session::get
    mock_session = mock(requests.Session)
    when(mock_session).get(ANY(str), ...).thenReturn(mock_response)

    # Mock Response::raise_for_status
    when(mock_response).raise_for_status().thenRaise(
        requests.ReadTimeout("Read timed out. (read timeout=0.05)")
    )

    # Setup
    client = ArtveeClient()
    client._session = mock_session

    # Test
    with pytest.raises(requests.Timeout):
        client.get_metadata(CategoryType.ABSTRACT, 5)

    verify(mock_session, times=1).get(...)
    verify(mock_response, times=1).raise_for_status()


def test_get_image():
    # Mock Response
    body = "dGVzdF9nZXRfaW1hZ2U="
    mock_response = mock(requests.Response)
    mock_response.content = body.encode("ascii")

    # Mock Session::get
    mock_session = mock(requests.Session)
    when(mock_session).get(
        "https://mdl.artvee.com/ft/55318pl.jpg", timeout=(3.05, 10)
    ).thenReturn(mock_response)

    # Mock Response::raise_for_status
    when(mock_response).raise_for_status().thenReturn(None)

    # Setup
    client = ArtveeClient()
    client._session = mock_session
    img_metadata = ImageMetadata(source_url="https://mdl.artvee.com/ft/55318pl.jpg")

    # Test
    result = client.get_image(img_metadata)

    # Validate
    assert body == result.decode("ascii"), "image is invalid"
    verify(mock_session, times=1).get(...)
    verify(mock_response, times=1).raise_for_status()


def test_get_image_raise_for_status():
    # Mock Response
    mock_response = mock(requests.Response)

    # Mock Session::get
    mock_session = mock(requests.Session)
    when(mock_session).get(ANY(str), ...).thenReturn(mock_response)

    # Mock Response::raise_for_status
    when(mock_response).raise_for_status().thenRaise(
        requests.ReadTimeout("Read timed out. (read timeout=0.05)")
    )

    # Setup
    client = ArtveeClient()
    client._session = mock_session
    img_metadata = ImageMetadata(source_url="https://mdl.artvee.com/ft/55318pl.jpg")

    # Test
    with pytest.raises(requests.Timeout):
        client.get_image(img_metadata)

    verify(mock_session, times=1).get(...)
    verify(mock_response, times=1).raise_for_status()
