"""
Provider for making API calls to the RoEx Tonn API
"""

import os
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, retry_if_result, before_sleep_log

# Initialize logger for this module
logger = logging.getLogger(__name__)

# Helper function for tenacity: Checks if the result has a retry-able status code
def should_retry_on_http_error(result: Any) -> bool:
    """Return True if the result is a Response object with a retry-able server error status code."""
    # Check if the result is actually a Response object
    if isinstance(result, requests.Response):
        return result.status_code in {500, 502, 503, 504}
    # If it's not a Response object (e.g., it's the parsed dict), it means success, so don't retry.
    return False


class ApiProvider:
    """Provider for making API calls to the RoEx Tonn API"""

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the API provider

        Args:
            base_url: Base URL for the API (e.g., "https://tonn.roexaudio.com")
            api_key: API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": api_key
        }
        logger.info(f"ApiProvider initialized for base URL: {self.base_url}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=(retry_if_exception_type(requests.exceptions.RequestException) | retry_if_result(should_retry_on_http_error)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API, handling retries and specific errors.

        Args:
            endpoint: API endpoint path (e.g., "/mixpreview")
            data: JSON payload for the request

        Returns:
            JSON response from the API

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, endpoint)
        logger.info(f"Making POST request to: {url}")
        logger.debug(f"Request data (keys): {list(data.keys())}")

        try:
            response = requests.post(url, json=data, headers=self.headers)
            logger.info(f"Received response with status code: {response.status_code} from {url}")

            # Check status *after* tenacity is done (if it didn't retry to success)
            if not response.ok:
                logger.warning(f"Non-OK ({response.status_code}) response from {url}. Response text: {response.text[:500]}...") # Log beginning of error text
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            # Try to parse as JSON, but handle non-JSON responses gracefully
            try:
                return response.json()
            except ValueError:
                return {"response": response.text}
        except requests.exceptions.RequestException as e:
            logger.exception(f"HTTP request failed: POST {url}. Error: {e}")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error occurred during request: POST {url}. Error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=(retry_if_exception_type(requests.exceptions.RequestException) | retry_if_result(should_retry_on_http_error)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def get(self, endpoint: str) -> Any:
        """
        Make a GET request to the API, handling retries and specific errors.

        Args:
            endpoint: API endpoint path (e.g., "/health")

        Returns:
            JSON response from the API or response text if not JSON

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, endpoint)
        logger.info(f"Making GET request to: {url}")

        try:
            response = requests.get(url, headers=self.headers)
            logger.info(f"Received response with status code: {response.status_code} from {url}")
            
            # Check status *after* tenacity is done (if it didn't retry to success)
            if not response.ok:
                logger.warning(f"Non-OK ({response.status_code}) response from {url}. Response text: {response.text[:500]}...") # Log beginning of error text
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            # Try to parse as JSON, but handle non-JSON responses gracefully
            try:
                return response.json()
            except ValueError: # Handle cases where API might return non-JSON on success
                 logger.warning(f"Response from GET {url} is not JSON. Returning raw text.")
                 return response.text # Or raise RoexApiException if JSON is always expected

        except requests.exceptions.RequestException as e:
            logger.exception(f"HTTP request failed: GET {url}. Error: {e}")
            raise
        except Exception as e:
            logger.exception(f"An unexpected error occurred during request: GET {url}. Error: {e}")
            raise

    def download_file(self, url: str, local_filename: str, chunk_size: int = 8192) -> bool:
        """
        Download a file from a URL to a local file

        Args:
            url: URL of the file to download
            local_filename: Path to save the downloaded file
            chunk_size: Size of chunks for streaming download

        Returns:
            True if download was successful, False otherwise
        """
        logger.info(f"Attempting to download file from {url} to {local_filename}")
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(local_filename)), exist_ok=True)

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
            logger.info(f"Successfully downloaded file to {local_filename}")
            return True
        except requests.exceptions.RequestException as e:
            logger.exception(f"Failed to download file from {url}. Error: {e}")
            return False
        except IOError as e:
            logger.exception(f"Failed to write downloaded file to {local_filename}. Error: {e}")
            return False
        except Exception as e:
            logger.exception(f"An unexpected error occurred during file download from {url}. Error: {e}")
            return False