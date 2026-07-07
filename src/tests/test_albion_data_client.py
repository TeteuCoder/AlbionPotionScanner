import httpx
import pytest
from src.clients.albion_data_client import (
    AlbionDataClient,
    AlbionAPIError,
    AlbionConnectionError,
    AlbionResponseValidationError
)
from src.domain.market_models import MarketPrice

# A simple custom transport for mocking httpx requests without mock libraries
class MockTransport(httpx.BaseTransport):
    def __init__(self, handler):
        self.handler = handler

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        return self.handler(request)


def test_fetch_price_single_item_success():
    """Verify that a successful request for a single item deserializes correctly."""
    mock_data = [
        {
            "item_id": "T4_POTION_HEAL",
            "quality": 1,
            "sell_price_min": 1000,
            "sell_price_min_date": "2026-07-06T12:00:00",
            "buy_price_max": 950,
            "buy_price_max_date": "2026-07-06T12:00:00"
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        # Check that we query Brecilien
        assert "locations=Brecilien" in str(request.url.query)
        # Check item ID in the path
        assert "T4_POTION_HEAL.json" in request.url.path
        return httpx.Response(200, json=mock_data)

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        prices = client.fetch_price("T4_POTION_HEAL")
        
        assert len(prices) == 1
        price = prices[0]
        assert isinstance(price, MarketPrice)
        assert price.item_id == "T4_POTION_HEAL"
        assert price.quality == 1
        assert price.sell_price_min == 1000
        assert price.sell_price_min_date == "2026-07-06T12:00:00"
        assert price.buy_price_max == 950
        assert price.buy_price_max_date == "2026-07-06T12:00:00"


def test_fetch_prices_multiple_items_success():
    """Verify that a successful request for multiple items (batching) queries the correct endpoint and deserializes correctly."""
    mock_data = [
        {
            "item_id": "T4_POTION_HEAL",
            "quality": 1,
            "sell_price_min": 1000,
            "sell_price_min_date": "2026-07-06T12:00:00",
            "buy_price_max": 950,
            "buy_price_max_date": "2026-07-06T12:00:00"
        },
        {
            "item_id": "T6_POTION_HEAL",
            "quality": 2,
            "sell_price_min": 5000,
            "sell_price_min_date": "2026-07-06T12:30:00",
            "buy_price_max": 4800,
            "buy_price_max_date": "2026-07-06T12:30:00"
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        # Check that we query Brecilien and qualities if passed
        assert "locations=Brecilien" in str(request.url.query)
        assert "qualities=1%2C2" in str(request.url.query)
        # Check batching format in the path
        assert "T4_POTION_HEAL,T6_POTION_HEAL.json" in request.url.path
        return httpx.Response(200, json=mock_data)

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        prices = client.fetch_prices(["T4_POTION_HEAL", "T6_POTION_HEAL"], qualities=[1, 2])
        
        assert len(prices) == 2
        assert prices[0].item_id == "T4_POTION_HEAL"
        assert prices[1].item_id == "T6_POTION_HEAL"
        assert prices[1].quality == 2


def test_empty_response():
    """Verify that an empty response array returning no prices is handled gracefully."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        prices = client.fetch_prices(["T4_POTION_HEAL"])
        assert prices == []


def test_malformed_json_response():
    """Verify that a response that is not valid JSON raises AlbionResponseValidationError."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content="Not a JSON string {")

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        with pytest.raises(AlbionResponseValidationError) as exc_info:
            client.fetch_prices(["T4_POTION_HEAL"])
        assert "Response is not valid JSON" in str(exc_info.value)


def test_malformed_response_not_an_array():
    """Verify that a response that is not a JSON list raises AlbionResponseValidationError."""
    def handler(request: httpx.Request) -> httpx.Response:
        # Returns an object instead of list
        return httpx.Response(200, json={"error": "Something went wrong"})

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        with pytest.raises(AlbionResponseValidationError) as exc_info:
            client.fetch_prices(["T4_POTION_HEAL"])
        assert "Expected a JSON array" in str(exc_info.value)


def test_invalid_item_structure_missing_fields():
    """Verify that a response containing items with missing fields raises AlbionResponseValidationError."""
    # 'sell_price_min' is missing
    bad_data = [
        {
            "item_id": "T4_POTION_HEAL",
            "quality": 1,
            "sell_price_min_date": "2026-07-06T12:00:00",
            "buy_price_max": 950,
            "buy_price_max_date": "2026-07-06T12:00:00"
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=bad_data)

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        with pytest.raises(AlbionResponseValidationError) as exc_info:
            client.fetch_prices(["T4_POTION_HEAL"])
        assert "Missing required field" in str(exc_info.value)
        assert "sell_price_min" in str(exc_info.value)


def test_invalid_item_structure_wrong_types():
    """Verify that a response containing items with fields of incorrect types raises AlbionResponseValidationError."""
    # 'quality' should be an integer, but is a non-numeric string here
    bad_data = [
        {
            "item_id": "T4_POTION_HEAL",
            "quality": "not-a-number",
            "sell_price_min": 1000,
            "sell_price_min_date": "2026-07-06T12:00:00",
            "buy_price_max": 950,
            "buy_price_max_date": "2026-07-06T12:00:00"
        }
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=bad_data)

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        with pytest.raises(AlbionResponseValidationError) as exc_info:
            client.fetch_prices(["T4_POTION_HEAL"])
        assert "Invalid field type" in str(exc_info.value)


def test_http_error_response():
    """Verify that a non-2xx status code response raises AlbionAPIError."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, content="Internal Server Error")

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        with pytest.raises(AlbionAPIError) as exc_info:
            client.fetch_prices(["T4_POTION_HEAL"])
        assert "API Error (HTTP 500)" in str(exc_info.value)
        assert exc_info.value.status_code == 500


def test_request_timeout():
    """Verify that a request timeout raises AlbionConnectionError."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("Mocked timeout message")

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        with pytest.raises(AlbionConnectionError) as exc_info:
            client.fetch_prices(["T4_POTION_HEAL"])
        assert "timed out" in str(exc_info.value)


def test_request_connection_error():
    """Verify that a general connection error raises AlbionConnectionError."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.RequestError("Mocked connection error", request=request)

    transport = MockTransport(handler)
    with httpx.Client(transport=transport) as mock_http_client:
        client = AlbionDataClient(http_client=mock_http_client)
        with pytest.raises(AlbionConnectionError) as exc_info:
            client.fetch_prices(["T4_POTION_HEAL"])
        assert "Failed to connect" in str(exc_info.value)


def test_invalid_input_parameters():
    """Verify that empty inputs (such as empty item_id or empty list values) raise value errors."""
    client = AlbionDataClient()
    
    # Empty items list returns empty list immediately
    assert client.fetch_prices([]) == []
    
    # List containing empty string ID raises ValueError
    with pytest.raises(ValueError):
        client.fetch_prices(["T4_POTION_HEAL", ""])
        
    with pytest.raises(ValueError):
        client.fetch_price("")
