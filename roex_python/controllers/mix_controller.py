"""
Controller for multitrack mixing operations
"""

import time
from typing import Dict, Any, List
import logging

import requests

from roex_python.models.mixing import (
    FinalMixRequest,
    FinalMixRequestAdvanced,
    FinalMixResult,
    MultitrackMixRequest,
    MultitrackTaskResponse,
    PreviewMixResult,
    TrackData,
    TrackGainData,
    TrackEffectsData
)
from roex_python.providers.api_provider import ApiProvider

# Initialize logger for this module
logger = logging.getLogger(__name__)

class MixController:
    """Controller for managing multitrack mixing operations via the RoEx API."""

    def __init__(self, api_provider: ApiProvider):
        """
        Initialize the MixController.

        Typically, this controller is accessed via `client.mix` rather than
        instantiated directly.

        Args:
            api_provider (ApiProvider): An instance of ApiProvider configured with
                the base URL and API key.
        """
        self.api_provider = api_provider
        logger.info("MixController initialized.")

    def create_mix_preview(self, request: MultitrackMixRequest) -> MultitrackTaskResponse:
        """
        Initiate a multitrack mix preview task.

        This method sends the track data and mixing parameters to the RoEx API
        to start an asynchronous mixing process. It returns immediately with a
        task ID, which can be used with `retrieve_preview_mix` to check the status
        and get the results once processing is complete.

        Args:
            request (MultitrackMixRequest): An object containing the list of tracks
                (TrackData) and mixing parameters (musical style, return stems, etc.).
                Track URLs must point to accessible WAV or FLAC files.

        Returns:
            MultitrackTaskResponse: An object containing the unique `multitrack_task_id`
                for the initiated preview task.

        Raises:
            requests.exceptions.RequestException: If the API request fails due to network
                                                 issues or invalid endpoint.
            Exception: If the API returns an error response (e.g., 4xx, 5xx status codes)
                       indicating issues like invalid input, authentication failure, or
                       server errors.

        Example:
            >>> from roex_python.models import TrackData, MultitrackMixRequest, MusicalStyle, InstrumentGroup
            >>> # Assume 'client' is an initialized RoExClient
            >>> # Assume 'track_url_1', 'track_url_2' are URLs obtained after uploading local files
            >>> tracks = [
            ...     TrackData(track_url=track_url_1, instrument_group=InstrumentGroup.BASS_GROUP),
            ...     TrackData(track_url=track_url_2, instrument_group=InstrumentGroup.VOCAL_GROUP)
            ... ]
            >>> mix_request = MultitrackMixRequest(
            ...     track_data=tracks,
            ...     musical_style=MusicalStyle.POP,
            ...     return_stems=False
            ... )
            >>> try:
            >>>     task_response = client.mix.create_mix_preview(mix_request)
            >>>     print(f"Mix preview task started: {task_response.multitrack_task_id}")
            >>>     # Proceed to poll using retrieve_preview_mix with this task_id
            >>> except Exception as e:
            >>>     print(f"Error starting mix preview: {e}")

        """
        logger.info("Creating mix preview")
        logger.debug(f"Mix request data: {request}")
        payload = self._prepare_mix_preview_payload(request)

        try:
            response = self.api_provider.post("/mixpreview", payload)
            logger.info(f"Mix preview created successfully. Task ID: {response.get('multitrack_task_id', '')}")
            return MultitrackTaskResponse(
                multitrack_task_id=response.get("multitrack_task_id", "")
            )
        except requests.HTTPError as e:
            # Log specific HTTP errors
            error_detail = f"{e.response.status_code} - {e.response.text}" if hasattr(e, 'response') and e.response else str(e)
            logger.error(f"HTTP error creating mix preview: {error_detail}")
            raise Exception(f"Failed to create mix preview: {error_detail}")
        except Exception as e:
            # Catch other potential exceptions (e.g., connection errors)
            logger.exception(f"Unexpected error creating mix preview: {e}")
            raise

    def retrieve_preview_mix(self, task_id: str, retrieve_fx_settings: bool = False,
                             max_attempts: int = 30, poll_interval: int = 5) -> PreviewMixResult:
        """
        Retrieve the results of a multitrack mix preview task, polling until complete.

        Polls the ``/retrievepreviewmix`` endpoint until the task reaches
        ``MIX_TASK_PREVIEW_COMPLETED`` or *max_attempts* is exhausted.

        Args:
            task_id (str): The ``multitrack_task_id`` from ``create_mix_preview``.
            retrieve_fx_settings (bool): Request detailed FX settings. Defaults to False.
            max_attempts (int): Maximum polling iterations. Defaults to 30.
            poll_interval (int): Seconds between polls. Defaults to 5.

        Returns:
            PreviewMixResult: A typed result containing:
                - ``download_url_preview_mixed`` (Optional[str]): Signed URL for the preview mix.
                - ``stems`` (Optional[Dict[str, str]]): Per-stem download URLs (if requested).
                - ``mix_output_settings`` (Optional[Dict]): Gain, pan, and other applied settings.
                - ``status`` (Optional[str]): Task status string.

        Raises:
            Exception: If the task does not complete within *max_attempts* polls.

        Example:
            >>> result = client.mix.retrieve_preview_mix(task_id)
            >>> print(result.download_url_preview_mixed)
        """
        logger.info(f"Retrieving preview mix for task ID: {task_id}")
        payload = {
            "multitrackData": {
                "multitrackTaskId": task_id,
                "retrieveFXSettings": retrieve_fx_settings
            }
        }

        def _parse_preview_result(raw: Dict[str, Any]) -> PreviewMixResult:
            return PreviewMixResult(
                download_url_preview_mixed=raw.get("download_url_preview_mixed"),
                stems=raw.get("stems"),
                mix_output_settings=raw.get("mix_output_settings"),
                status=raw.get("status"),
            )

        try:
            response = self.api_provider.post("/retrievepreviewmix", payload)

            if "previewMixTaskResults" in response and response.get("status") == "MIX_TASK_PREVIEW_COMPLETED":
                logger.info(f"Preview mix for task {task_id} is ready.")
                return _parse_preview_result(response["previewMixTaskResults"])

            if "status" in response and response.get("status") != "MIX_TASK_PREVIEW_COMPLETED":
                logger.info(f"Mix preview is pending. Starting polling...")
            else:
                return _parse_preview_result(response)
        except requests.HTTPError:
            logger.error("Initial request failed. Starting polling...")
            pass

        for attempt in range(max_attempts):
            try:
                logger.debug(f"Polling attempt {attempt + 1}/{max_attempts}...")
                response = self.api_provider.post("/retrievepreviewmix", payload)

                if "previewMixTaskResults" in response:
                    results = response["previewMixTaskResults"]
                    status = results.get("status", "")
                    if status == "MIX_TASK_PREVIEW_COMPLETED":
                        logger.info(f"Preview mix for task {task_id} is ready.")
                        return _parse_preview_result(results)

                if "status" in response:
                    logger.info(f"Current status: {response.get('status')}")
            except requests.HTTPError as e:
                logger.error(f"Error during polling: {str(e)}")

            time.sleep(poll_interval)

        logger.error(f"Polling timed out for preview mix task {task_id} after {max_attempts} attempts.")
        raise Exception(f"Preview mix task {task_id} did not complete after polling for {max_attempts * poll_interval} seconds.")

    def retrieve_final_mix_advanced(self, request: FinalMixRequestAdvanced) -> FinalMixResult:
        """
        Retrieve the final multitrack mix with advanced audio effects (EQ, compression, panning).

        Posts to ``/retrievefinalmix`` with per-track EQ, compression, and panning
        settings.  Typically follows ``create_mix_preview`` / ``retrieve_preview_mix``.

        Args:
            request (FinalMixRequestAdvanced): Advanced final mix parameters including
                per-track EQ, compression, panning, gain, and global options.

        Returns:
            FinalMixResult: A typed result containing:
                - ``download_url_mixed`` (Optional[str]): Signed URL for the final mix.
                - ``stems`` (Optional[Dict[str, str]]): Per-stem download URLs (if requested).
                - ``mix_output_settings`` (Optional[Dict]): Applied settings.

        Raises:
            Exception: If the API returns an error response.

        Example:
            >>> result = client.mix.retrieve_final_mix_advanced(request)
            >>> print(result.download_url_mixed)
        """
        logger.info(f"Retrieving advanced final mix for task ID: {request.multitrack_task_id}")
        logger.debug(f"Advanced final mix request data: {request}")
        payload = self._prepare_advanced_final_mix_payload(request)

        try:
            response = self.api_provider.post("/retrievefinalmix", payload)
            logger.info("Advanced final mix retrieved successfully.")
            raw = response.get("applyAudioEffectsResults", response)
            return FinalMixResult(
                download_url_mixed=raw.get("download_url_mixed"),
                stems=raw.get("stems"),
                mix_output_settings=raw.get("mix_output_settings"),
            )
        except requests.HTTPError as e:
            error_detail = f"{e.response.status_code} - {e.response.text}" if hasattr(e, 'response') and e.response else str(e)
            logger.error(f"HTTP error retrieving advanced final mix: {error_detail}")
            raise Exception(f"Failed to retrieve advanced final mix: {error_detail}")
        except Exception as e:
            logger.exception(f"Unexpected error retrieving advanced final mix: {e}")
            raise

    def retrieve_final_mix(self, request: FinalMixRequest) -> FinalMixResult:
        """
        Retrieve the final multitrack mix, potentially with gain adjustments.

        Posts to ``/retrievefinalmix`` with optional per-track gain changes applied
        on top of the original preview.

        Args:
            request (FinalMixRequest): Final mix parameters including the preview
                task ID, optional gain adjustments, and stem / sample-rate options.

        Returns:
            FinalMixResult: A typed result containing:
                - ``download_url_mixed`` (Optional[str]): Signed URL for the final mix.
                - ``stems`` (Optional[Dict[str, str]]): Per-stem download URLs (if requested).
                - ``mix_output_settings`` (Optional[Dict]): Applied settings.

        Raises:
            Exception: If the API returns an error response.

        Example:
            >>> result = client.mix.retrieve_final_mix(request)
            >>> print(result.download_url_mixed)
        """
        logger.info(f"Retrieving final mix for task ID: {request.multitrack_task_id}")
        logger.debug(f"Final mix request data: {request}")
        payload = self._prepare_final_mix_payload(request)

        try:
            response = self.api_provider.post("/retrievefinalmix", payload)
            logger.info("Final mix retrieved successfully.")
            raw = response.get("applyAudioEffectsResults", response)
            return FinalMixResult(
                download_url_mixed=raw.get("download_url_mixed"),
                stems=raw.get("stems"),
                mix_output_settings=raw.get("mix_output_settings"),
            )
        except requests.HTTPError as e:
            error_detail = f"{e.response.status_code} - {e.response.text}" if hasattr(e, 'response') and e.response else str(e)
            logger.error(f"HTTP error retrieving final mix: {error_detail}")
            raise Exception(f"Failed to retrieve final mix: {error_detail}")
        except Exception as e:
            logger.exception(f"Unexpected error retrieving final mix: {e}")
            raise

    def _prepare_mix_preview_payload(self, request: MultitrackMixRequest) -> Dict[str, Any]:
        """
        Convert the model to API payload for mix preview

        Args:
            request (MultitrackMixRequest): Multitrack mix request

        Returns:
            API payload dictionary
        """
        logger.debug("Preparing mix preview payload")
        track_data = []
        for track in request.track_data:
            track_data.append({
                "trackURL": track.track_url,
                "instrumentGroup": track.instrument_group.value,
                "presenceSetting": track.presence_setting.value,
                "panPreference": track.pan_preference.value,
                "reverbPreference": track.reverb_preference.value
            })

        data = {
            "trackData": track_data,
            "musicalStyle": request.musical_style.value,
            "returnStems": request.return_stems,
            "sampleRate": request.sample_rate,
        }
        if request.webhook_url is not None:
            data["webhookURL"] = request.webhook_url
        return {"multitrackData": data}

    def _prepare_final_mix_payload(self, request: FinalMixRequest) -> Dict[str, Any]:
        """
        Convert the model to API payload for final mix

        Args:
            request (FinalMixRequest): Final mix request

        Returns:
            API payload dictionary
        """
        logger.debug("Preparing final mix payload")
        track_data = []
        for track in request.track_data:
            track_data.append({
                "trackURL": track.track_url,
                "gainDb": track.gain_db
            })

        return {
            "applyAudioEffectsData": {
                "multitrackTaskId": request.multitrack_task_id,
                "trackData": track_data,
                "returnStems": request.return_stems,
                "sampleRate": request.sample_rate
            }
        }

    def _prepare_advanced_final_mix_payload(self, request: FinalMixRequestAdvanced) -> Dict[str, Any]:
        """
        Convert the advanced model to API payload for final mix with audio effects

        Args:
            request (FinalMixRequestAdvanced): Advanced final mix request with audio effects

        Returns:
            API payload dictionary with EQ, compression, and panning settings
        """
        logger.debug("Preparing advanced final mix payload with audio effects")
        track_data = []
        
        for track in request.track_data:
            track_dict = {
                "trackURL": track.track_url,
                "gainDb": track.gain_db
            }
            
            # Add panning settings if present
            if track.panning_settings is not None:
                track_dict["panning_settings"] = {
                    "panning_angle": track.panning_settings.panning_angle
                }
            
            # Add EQ settings if present
            if track.eq_settings is not None:
                eq_dict = {}
                for band_num in range(1, 7):
                    band_attr = f"band_{band_num}"
                    band = getattr(track.eq_settings, band_attr)
                    if band is not None:
                        eq_dict[band_attr] = {
                            "gain": band.gain,
                            "q": band.q,
                            "centre_freq": band.centre_freq
                        }
                
                if eq_dict:  # Only add if at least one band is configured
                    track_dict["eq_settings"] = eq_dict
            
            # Add compression settings if present
            if track.compression_settings is not None:
                track_dict["compression_settings"] = {
                    "threshold": track.compression_settings.threshold,
                    "ratio": track.compression_settings.ratio,
                    "attack_ms": track.compression_settings.attack_ms,
                    "release_ms": track.compression_settings.release_ms
                }
            
            track_data.append(track_dict)

        payload = {
            "applyAudioEffectsData": {
                "multitrackTaskId": request.multitrack_task_id,
                "trackData": track_data,
                "returnStems": request.return_stems,
                "createMaster": request.create_master,
                "sampleRate": request.sample_rate
            }
        }
        
        # Add optional desired loudness
        if request.desired_loudness is not None:
            payload["applyAudioEffectsData"]["desiredLoudness"] = request.desired_loudness.value
        
        # Add optional webhook URL
        if request.webhook_url is not None:
            payload["applyAudioEffectsData"]["webhookURL"] = request.webhook_url
        
        return payload