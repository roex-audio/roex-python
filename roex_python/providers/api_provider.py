"""
Provider for making API calls to the RoEx Tonn API
"""

import os
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests


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

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a POST request to the API

        Args:
            endpoint: API endpoint path (e.g., "/mixpreview")
            data: JSON payload for the request

        Returns:
            JSON response from the API

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, endpoint)
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()

        # Try to parse as JSON, but handle non-JSON responses gracefully
        try:
            return response.json()
        except ValueError:
            return {"response": response.text}

    def get(self, endpoint: str) -> Any:
        """
        Make a GET request to the API

        Args:
            endpoint: API endpoint path (e.g., "/health")

        Returns:
            JSON response from the API or response text if not JSON

        Raises:
            requests.HTTPError: If the request fails
        """
        url = urljoin(self.base_url, endpoint)
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        # Try to parse as JSON, but handle non-JSON responses gracefully
        try:
            return response.json()
        except ValueError:
            return response.text

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
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(local_filename)), exist_ok=True)

        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        f.write(chunk)
            return True
        except Exception as e:
            print(f"Error downloading file from {url}: {e}")
            return False