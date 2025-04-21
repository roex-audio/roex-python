"""Utility functions for the RoEx package."""

import os
import requests
from typing import Dict, Optional
import logging

from .client import RoExClient
from .models import UploadUrlRequest

# Initialize logger for this module
logger = logging.getLogger(__name__)

def get_content_type(file_path: str) -> str:
    """Determine content type based on file extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        The MIME content type for the file
        
    Raises:
        ValueError: If the file extension is not supported
    """
    extension = os.path.splitext(file_path)[1].lower()
    content_type_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac'
    }
    if extension not in content_type_map:
        raise ValueError(f"Unsupported file type: {extension}. Must be one of: {', '.join(content_type_map.keys())}")
    return content_type_map[extension]


def upload_file(client: RoExClient, file_path: str) -> str:
    """Upload a file and return its readable URL.
    
    Args:
        client: RoExClient instance
        file_path: Path to the file to upload
        
    Returns:
        The URL where the uploaded file can be accessed
        
    Raises:
        Exception: If the upload fails
    """
    logger.info(f"Starting upload process for file: {file_path}")
    filename = os.path.basename(file_path)
    content_type = get_content_type(file_path)
    
    # Get upload URLs
    try:
        logger.info(f"Requesting upload URL for {filename}...")
        request = UploadUrlRequest(filename=filename, content_type=content_type)
        response = client.upload.get_upload_url(request)
        
        if response.error:
            logger.error(f"Failed to get upload URL: {response.message}")
            raise ValueError("Failed to get valid upload URL response from RoEx API.")
        logger.info("Successfully received upload URL.")
    except Exception as e:
        logger.exception(f"Error getting upload URL for {filename}: {e}")
        raise # Re-raise the exception after logging

    # Upload the file
    try:
        logger.info(f"Attempting to upload {filename} to upload URL...")
        with open(file_path, 'rb') as f:
            upload_response = requests.put(
                response.signed_url,
                data=f,
                headers={'Content-Type': content_type}
            )
            upload_response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        logger.info(f"Successfully uploaded {filename}. Readable URL: {response.readable_url}")
        return response.readable_url
    except requests.exceptions.RequestException as e:
        logger.exception(f"HTTP error during file upload for {filename}: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during file upload for {filename}: {e}")
        raise
