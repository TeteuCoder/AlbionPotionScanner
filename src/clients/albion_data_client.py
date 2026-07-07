import httpx
from typing import List, Optional
from src.domain.market_models import MarketPrice

class AlbionDataClientException(Exception):
    """Base exception for all errors related to the Albion Data Client."""
    pass

class AlbionAPIError(AlbionDataClientException):
    """Raised when the API returns a non-2xx status code response."""
    def __init__(self, message: str, status_code: int):
        super().__init__(f"API Error (HTTP {status_code}): {message}")
        self.status_code = status_code

class AlbionConnectionError(AlbionDataClientException):
    """Raised when a network connection error or timeout occurs."""
    pass

class AlbionResponseValidationError(AlbionDataClientException):
    """Raised when the API response structure is invalid, malformed, or missing required fields."""
    pass


class AlbionDataClient:
    """
    Client for interacting with the Albion Online Data Project API to fetch market prices.

    This client restricts queries to Brecilien as required by the Version 1 specification.
    The city is hardcoded and cannot be configured.

    Why batching is preferred:
    --------------------------
    The Albion Online Data Project API supports querying multiple items in a single HTTP request by
    providing a comma-separated list of item IDs. Batching is highly preferred because:
    1. It reduces network latency and overhead by making one HTTP call instead of multiple individual calls.
    2. It prevents rate-limiting and IP banning from the community-run public API endpoint.
    3. It improves performance during scans that need to evaluate multiple potion families and tiers.
    """

    DEFAULT_BASE_URL = "https://west.albion-online-data.com"
    TIMEOUT_SECONDS = 10.0

    def __init__(self, base_url: str = DEFAULT_BASE_URL, http_client: Optional[httpx.Client] = None):
        """
        Initializes the client.

        Args:
            base_url: The API base URL. Defaults to the Americas/West endpoint.
            http_client: An optional pre-configured httpx.Client to support dependency injection.
        """
        self.base_url = base_url.rstrip("/")
        # If an external client is injected, we use it; otherwise we create and manage a shared client.
        self._http_client = http_client or httpx.Client()
        self._owns_client = http_client is None

    def fetch_prices(self, item_ids: List[str], qualities: Optional[List[int]] = None) -> List[MarketPrice]:
        """
        Fetches current Brecilien market prices for a list of item IDs.

        This method queries the documented '/api/v2/stats/prices/{item_ids}.json' endpoint.
        The location parameter is hardcoded to 'Brecilien'.

        Args:
            item_ids: A list of Albion item ID strings (e.g. ["T4_BAG", "T4_POTION_HEAL"]).
            qualities: Optional list of integer quality levels (e.g. [1, 2]).

        Returns:
            A list of immutable MarketPrice objects.
        """
        if not item_ids:
            return []

        # Validate that item_ids doesn't contain empty/null values
        if any(not item_id for item_id in item_ids):
            raise ValueError("item_ids list cannot contain empty strings")

        # Comma-separate the item IDs as supported by the batch endpoint
        item_ids_str = ",".join(item_ids)
        url = f"{self.base_url}/api/v2/stats/prices/{item_ids_str}.json"

        # Force location to Brecilien
        params = {"locations": "Brecilien"}
        if qualities:
            params["qualities"] = ",".join(map(str, qualities))

        try:
            response = self._http_client.get(
                url,
                params=params,
                timeout=self.TIMEOUT_SECONDS
            )
        except httpx.TimeoutException as e:
            raise AlbionConnectionError(f"Request to Albion API timed out: {e}") from e
        except httpx.RequestError as e:
            raise AlbionConnectionError(f"Failed to connect to Albion API: {e}") from e

        if response.status_code != 200:
            raise AlbionAPIError(response.text, response.status_code)

        try:
            data = response.json()
        except ValueError as e:
            raise AlbionResponseValidationError(f"Response is not valid JSON: {e}") from e

        if not isinstance(data, list):
            raise AlbionResponseValidationError("Expected a JSON array from prices endpoint")

        prices = []
        for idx, obj in enumerate(data):
            if not isinstance(obj, dict):
                raise AlbionResponseValidationError(
                    f"Expected object at index {idx} in response array, got {type(obj).__name__}"
                )

            # Check required fields
            required_fields = [
                "item_id", "quality", "sell_price_min",
                "sell_price_min_date", "buy_price_max", "buy_price_max_date"
            ]
            for field in required_fields:
                if field not in obj:
                    raise AlbionResponseValidationError(
                        f"Missing required field '{field}' in response item at index {idx}"
                    )

            try:
                # API returns 0 or nulls for missing values, handle types cleanly
                price = MarketPrice(
                    item_id=str(obj["item_id"]),
                    quality=int(obj["quality"]),
                    sell_price_min=int(obj["sell_price_min"]),
                    sell_price_min_date=str(obj["sell_price_min_date"]),
                    buy_price_max=int(obj["buy_price_max"]),
                    buy_price_max_date=str(obj["buy_price_max_date"])
                )
                prices.append(price)
            except (ValueError, TypeError) as e:
                raise AlbionResponseValidationError(
                    f"Invalid field type in response item at index {idx}: {e}"
                ) from e

        return prices

    def fetch_price(self, item_id: str, qualities: Optional[List[int]] = None) -> List[MarketPrice]:
        """
        Helper method to fetch current Brecilien market prices for a single item.

        Args:
            item_id: An Albion item ID string (e.g. 'T4_POTION_HEAL').
            qualities: Optional list of integer quality levels.

        Returns:
            A list of immutable MarketPrice objects.
        """
        if not item_id:
            raise ValueError("item_id cannot be empty")
        return self.fetch_prices([item_id], qualities)

    def close(self) -> None:
        """Closes the underlying HTTP client if it was created internally."""
        if self._owns_client:
            self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
