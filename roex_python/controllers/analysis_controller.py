"""
Controller for mix/master analysis operations
"""

from typing import Dict, Any, List

import requests
import logging

from roex_python.models.analysis import MixAnalysisRequest, AnalysisMusicalStyle
from roex_python.providers.api_provider import ApiProvider

# Initialize logger for this module
logger = logging.getLogger(__name__)

class AnalysisController:
    """Controller for submitting audio tracks for analysis and comparison via the RoEx API."""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the AnalysisController.

        Typically, this controller is accessed via `client.analysis` rather than
        instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("AnalysisController initialized.")

    def analyze_mix(self, request: MixAnalysisRequest) -> Dict[str, Any]:
        """
        Analyze a single mix or master track to retrieve detailed metrics.

        This method sends the track URL and analysis parameters to the API
        and returns the analysis results synchronously.

        Args:
            request (MixAnalysisRequest): An object containing the track URL
                (`audio_file_location`), the musical style for reference
                (`musical_style`), and whether the track is mastered (`is_master`).
                The URL must point to an accessible WAV or FLAC file.

        Returns:
            Dict[str, Any]: A dictionary containing the analysis results.
                The structure typically includes detailed metrics under a 'payload' key,
                covering loudness, dynamics, stereo field, phase, tonal balance, etc.
                Check the official RoEx API documentation for the full structure.

        Raises:
            requests.exceptions.RequestException: If the API request fails due to network
                                                 issues or invalid endpoint.
            Exception: If the API returns an error response (e.g., 4xx, 5xx status codes)
                       indicating issues like invalid input, file access problems, or
                       server errors.

        Example:
            >>> from roex_python.models import MixAnalysisRequest, AnalysisMusicalStyle
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'track_url' is a URL obtained after uploading a local file
            >>> analysis_request = MixAnalysisRequest(
            ...     audio_file_location=track_url,
            ...     musical_style=AnalysisMusicalStyle.ROCK_PUNK,
            ...     is_master=False
            ... )
            >>> try:
            >>>     analysis_results = client.analysis.analyze_mix(analysis_request)
            >>>     print(f"Analysis Loudness (LUFS): {analysis_results.get('payload', {}).get('integrated_loudness_lufs')}")
            >>>     # Explore other metrics in analysis_results['payload']
            >>> except Exception as e:
            >>>     print(f"Error analyzing mix: {e}")
        """
        logger.info(f"Analyzing mix with parameters: {request}")
        payload = {
            "mixDiagnosisData": {
                "audioFileLocation": request.audio_file_location,
                "musicalStyle": request.musical_style.value,
                "isMaster": request.is_master
            }
        }

        try:
            logger.debug(f"Sending analysis request to API: {payload}")
            response = self.api_provider.post("/mixanalysis", payload)
            if "mixDiagnosisResults" in response:
                logger.info("Analysis results received successfully.")
                return response["mixDiagnosisResults"]
            logger.info("Analysis results received without expected format.")
            return response
        except requests.HTTPError as e:
            logger.error(f"Failed to analyze mix: {str(e)}")
            raise Exception(f"Failed to analyze mix: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error analyzing mix: {e}")
            raise

    def compare_mixes(self, mix_a_url: str, mix_b_url: str,
                      musical_style: AnalysisMusicalStyle, is_master: bool = False) -> Dict[str, Any]:
        """
        Analyze two mixes and provide a comparison of their key metrics.

        This method internally calls `analyze_mix` for both provided track URLs
        and then computes differences between key metrics.

        Args:
            mix_a_url (str): URL of the first mix (must be accessible WAV/FLAC).
            mix_b_url (str): URL of the second mix (must be accessible WAV/FLAC).
            musical_style (AnalysisMusicalStyle): The musical style reference for analysis.
            is_master (bool, optional): Whether the tracks should be analyzed as
                mastered tracks. Defaults to False.

        Returns:
            Dict[str, Any]: A dictionary containing 'mix_a' results, 'mix_b' results, 
                          and calculated 'differences' between key metrics (loudness, etc.).

        Raises:
            requests.exceptions.RequestException: If either underlying `analyze_mix` call fails
                                                 due to network issues.
            Exception: If either underlying `analyze_mix` call returns an API error,
                       or if there's an issue during metric extraction/comparison.

        Example:
            >>> from roex_python.models import AnalysisMusicalStyle
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'track_url_a', 'track_url_b' are URLs for two mixes
            >>> try:
            >>>     comparison = client.analysis.compare_mixes(
            ...         mix_a_url=track_url_a,
            ...         mix_b_url=track_url_b,
            ...         musical_style=AnalysisMusicalStyle.POP,
            ...         is_master=True
            ...     )
            >>>     print(f"Mix A LUFS: {comparison['mix_a'].get('integrated_loudness_lufs')}")
            >>>     print(f"Mix B LUFS: {comparison['mix_b'].get('integrated_loudness_lufs')}")
            >>>     print(f"LUFS Difference: {comparison['differences'].get('integrated_loudness_lufs')}")
            >>>     # Explore other comparison metrics
            >>> except Exception as e:
            >>>     print(f"Error comparing mixes: {e}")
        """
        logger.info(f"Comparing mixes: {mix_a_url} and {mix_b_url} with musical style: {musical_style}")
        request_a = MixAnalysisRequest(
            audio_file_location=mix_a_url,
            musical_style=musical_style,
            is_master=is_master
        )

        request_b = MixAnalysisRequest(
            audio_file_location=mix_b_url,
            musical_style=musical_style,
            is_master=is_master
        )

        results_a = self.analyze_mix(request_a)
        results_b = self.analyze_mix(request_b)

        # Extract key metrics for comparison
        comparison = {
            "mix_a": self._extract_metrics(results_a),
            "mix_b": self._extract_metrics(results_b),
            "differences": self._compare_metrics(results_a, results_b)
        }

        logger.info("Comparison results generated successfully.")
        return comparison

    def _extract_metrics(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key metrics from diagnosis results

        Args:
            diagnosis: Mix diagnosis results

        Returns:
            Dictionary of extracted metrics
        """
        logger.debug(f"Extracting metrics from diagnosis results: {diagnosis}")
        payload = diagnosis.get("payload", {})

        # Extract production metrics
        production_keys = [
            "bit_depth", "clipping", "if_master_drc", "if_master_loudness",
            "if_mix_drc", "if_mix_loudness", "integrated_loudness_lufs", "mix_style",
            "mono_compatible", "musical_style", "peak_loudness_dbfs", "phase_issues",
            "sample_rate", "stereo_field"
        ]
        metrics = {key: payload.get(key, "N/A") for key in production_keys}

        # Add tonal profile
        metrics["tonal_profile"] = payload.get("tonal_profile", {})

        logger.info("Metrics extracted successfully.")
        return metrics

    def _compare_metrics(self, results_a: Dict[str, Any], results_b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare metrics between two analysis results

        Args:
            results_a: First mix diagnosis results
            results_b: Second mix diagnosis results

        Returns:
            Dictionary of differences
        """
        logger.info("Comparing metrics between two analysis results.")
        metrics_a = self._extract_metrics(results_a)
        metrics_b = self._extract_metrics(results_b)

        differences = {}

        # Compare numeric values
        numeric_keys = ["integrated_loudness_lufs", "peak_loudness_dbfs", "bit_depth", "sample_rate"]
        for key in numeric_keys:
            try:
                val_a = float(metrics_a.get(key, 0))
                val_b = float(metrics_b.get(key, 0))
                differences[key] = {
                    "difference": abs(val_a - val_b),
                    "mix_a_value": val_a,
                    "mix_b_value": val_b
                }
            except (ValueError, TypeError):
                differences[key] = "N/A"

        # Compare categorical values
        categorical_keys = ["clipping", "if_master_drc", "if_master_loudness", "stereo_field"]
        for key in categorical_keys:
            val_a = metrics_a.get(key)
            val_b = metrics_b.get(key)
            differences[key] = {
                "status": "SAME" if val_a == val_b else "DIFFERENT",
                "mix_a_value": val_a,
                "mix_b_value": val_b
            }

        # Compare tonal profiles
        tonal_a = metrics_a.get("tonal_profile", {})
        tonal_b = metrics_b.get("tonal_profile", {})
        tonal_diff = {}

        for freq in ["bass_frequency", "low_mid_frequency", "high_mid_frequency", "high_frequency"]:
            val_a = tonal_a.get(freq)
            val_b = tonal_b.get(freq)
            tonal_diff[freq] = {
                "status": "SAME" if val_a == val_b else "DIFFERENT",
                "mix_a_value": val_a,
                "mix_b_value": val_b
            }

        differences["tonal_profile"] = tonal_diff

        logger.info("Metrics comparison completed successfully.")
        return differences