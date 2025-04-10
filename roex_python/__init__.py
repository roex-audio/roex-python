"""
RoEx MCP - Model-Controller-Provider client for the RoEx Tonn API

This package provides a clean, type-safe interface to interact with the RoEx Tonn API
for audio mixing, mastering, analysis, and enhancement.
"""

__version__ = "0.1.0"
__author__ = "RoEx Audio"
__email__ = "support@roexaudio.com"
__license__ = "MIT"

from roex_python.client import RoExClient

__all__ = ["RoExClient"]