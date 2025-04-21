"""Example demonstrating how to use the upload functionality"""

import os
import requests
from roex_python import RoExClient
from roex_python.models import UploadUrlRequest

def get_upload_url(filename: str, content_type: str, api_key: str) -> dict:
    """
    Get signed URLs for uploading and accessing an audio file.
    
    Args:
        filename: Name of the file to upload
        content_type: MIME type of the file (audio/mpeg, audio/wav, or audio/flac)
        api_key: Your RoEx API key
    
    Returns:
        Dictionary containing signed_url and readable_url
    """
    client = RoExClient(api_key=api_key)
    
    request = UploadUrlRequest(
        filename=filename,
        content_type=content_type
    )
    
    response = client.upload.get_upload_url(request)
    
    if response.error:
        raise Exception(f"Failed to get upload URL: {response.message}")
    
    return {
        'signed_url': response.signed_url,
        'readable_url': response.readable_url
    }

def upload_file(signed_url: str, filename: str, content_type: str) -> bool:
    """
    Upload a file using the signed URL.
    
    Args:
        signed_url: The URL to upload the file to
        filename: Path to the file to upload
        content_type: MIME type of the file
    
    Returns:
        True if upload was successful
    """
    with open(filename, 'rb') as f:
        response = requests.put(
            signed_url,
            data=f,
            headers={'Content-Type': content_type}
        )
    return response.status_code == 200

def get_content_type(file_path: str) -> str:
    """
    Determine content type based on file extension.
    
    Args:
        file_path: Path to the file
    
    Returns:
        MIME type of the file
    """
    filename = os.path.basename(file_path)
    extension = os.path.splitext(filename)[1].lower()
    
    content_type_map = {
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.flac': 'audio/flac'
    }
    
    if extension not in content_type_map:
        raise ValueError(f"Unsupported file type: {extension}. Must be one of: {', '.join(content_type_map.keys())}")
    
    return content_type_map[extension]

if __name__ == "__main__":
    # Replace with your API key
    API_KEY = "AIzaSyCd-uoRDeMbXek_vKn9w09FejwsTIRmlyQ"
    
    # Example usage
    try:
        file_path = "/Users/davidronan/Desktop/demucs_A.mp3"
        content_type = get_content_type(file_path)
        
        # Get upload URLs
        result = get_upload_url(os.path.basename(file_path), content_type, API_KEY)
        
        # Upload the file
        success = upload_file(
            result['signed_url'],
            file_path,
            content_type
        )
        
        if success:
            print("File uploaded successfully!")
            print(f"Use this URL in other API calls: {result['readable_url']}")
        else:
            print("Upload failed")
            
    except Exception as e:
        print(f"Error: {str(e)}")
