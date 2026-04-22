"""
Controller for mix/master analysis operations
"""

from typing import Dict, Any, List

import requests
import logging

from roex_python.models.analysis import AnalysisMusicalStyle, AnalysisResult, MixAnalysisRequest
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

    def analyze_mix(self, request: MixAnalysisRequest) -> AnalysisResult:
        """
        Analyze a single mix or master track to retrieve detailed metrics.

        Sends the track URL and analysis parameters to ``/mixanalysis`` and
        returns the results synchronously.

        Args:
            request (MixAnalysisRequest): The track URL, musical style reference,
                and ``is_master`` flag.

        Returns:
            AnalysisResult: A typed result containing:
                - ``payload`` (Optional[Dict[str, Any]]): Diagnosis metrics including
                  ``integrated_loudness_lufs``, ``peak_loudness_dbfs``,
                  ``tonal_profile``, ``clipping``, ``stereo_field``, ``phase_issues``,
                  ``bit_depth``, ``sample_rate``, etc.
                - ``error`` (bool): Whether the analysis encountered an error.
                - ``info`` (str): Additional information from the API.
                - ``completion_time`` (str): When the analysis finished.

        Raises:
            Exception: If the API returns an error response.

        Example:
            >>> result = client.analysis.analyze_mix(request)
            >>> print(result.payload.get("integrated_loudness_lufs"))
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
            raw = response.get("mixDiagnosisResults", response)
            logger.info("Analysis results received successfully.")
            return AnalysisResult(
                payload=raw.get("payload"),
                error=raw.get("error", False),
                info=raw.get("info", ""),
                completion_time=raw.get("completion_time", ""),
            )
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

        Calls ``analyze_mix`` for both URLs and computes per-metric differences.

        Args:
            mix_a_url (str): URL of the first mix (accessible WAV/FLAC).
            mix_b_url (str): URL of the second mix (accessible WAV/FLAC).
            musical_style (AnalysisMusicalStyle): Musical style reference for analysis.
            is_master (bool): Whether to analyze as mastered tracks. Defaults to False.

        Returns:
            Dict[str, Any]: ``{"mix_a": {...}, "mix_b": {...}, "differences": {...}}``.

        Raises:
            Exception: If either underlying ``analyze_mix`` call fails.

        Example:
            >>> comparison = client.analysis.compare_mixes(url_a, url_b, AnalysisMusicalStyle.POP)
            >>> print(comparison["differences"]["integrated_loudness_lufs"])
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

        comparison = {
            "mix_a": self._extract_metrics(results_a),
            "mix_b": self._extract_metrics(results_b),
            "differences": self._compare_metrics(results_a, results_b)
        }

        logger.info("Comparison results generated successfully.")
        return comparison

    def _extract_metrics(self, diagnosis: AnalysisResult) -> Dict[str, Any]:
        """Extract key metrics from an AnalysisResult."""
        logger.debug(f"Extracting metrics from diagnosis results: {diagnosis}")
        payload = diagnosis.payload or {}

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

    def _compare_metrics(self, results_a: AnalysisResult, results_b: AnalysisResult) -> Dict[str, Any]:
        """Compare metrics between two AnalysisResult objects."""
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