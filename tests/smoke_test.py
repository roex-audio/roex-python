"""
Smoke test for roex-python SDK v1.3.1
Validates that models, enums, and payloads are accepted by the live API.
Run: ROEX_API_KEY=<key> python -m tests.smoke_test
"""

import os
import sys
import time

def main():
    api_key = os.getenv("ROEX_API_KEY")
    if not api_key:
        print("FAIL: ROEX_API_KEY not set")
        sys.exit(1)

    failures = []

    # --- 1. Import check ---
    print("[1/6] Import check...", end=" ")
    try:
        from roex_python.client import RoExClient
        from roex_python.models import (
            MixAnalysisRequest, AnalysisMusicalStyle,
            MixEnhanceRequest, EnhanceMusicalStyle,
            AudioCleanupData, SoundSource,
            LoudnessPreference, UploadUrlRequest,
        )
        from roex_python.utils import upload_file
        import roex_python
        assert roex_python.__version__ == "1.3.1"
        print(f"OK (v{roex_python.__version__})")
    except Exception as e:
        print(f"FAIL: {e}")
        failures.append(("Import check", e))
        print("\nCannot proceed without imports. Exiting.")
        sys.exit(1)

    # --- 2. Enum validation ---
    print("[2/6] Enum validation...", end=" ")
    try:
        assert hasattr(EnhanceMusicalStyle, "ROCK_INDIE")
        assert hasattr(EnhanceMusicalStyle, "GRITTY_CRUNCHY")
        assert hasattr(EnhanceMusicalStyle, "BALANCED")
        assert not hasattr(EnhanceMusicalStyle, "TECHNO")
        assert len(EnhanceMusicalStyle) == 18

        assert hasattr(AnalysisMusicalStyle, "AIRY_EXPANSIVE")
        assert hasattr(AnalysisMusicalStyle, "AGGRESSIVE")
        assert not hasattr(AnalysisMusicalStyle, "DANCE")

        assert hasattr(SoundSource, "BACKING_VOX_GROUP")
        assert hasattr(SoundSource, "BRASS_GROUP")
        assert not hasattr(SoundSource, "BACKING_VOCALS_GROUP")

        assert hasattr(LoudnessPreference, "NO_CHANGE")

        req = MixEnhanceRequest(
            audio_file_location="https://example.com/test.wav",
            musical_style=EnhanceMusicalStyle.POP,
        )
        assert req.loudness_preference == LoudnessPreference.NO_CHANGE
        assert req.get_processed_stems is False
        assert not hasattr(req, "fix_drc_issues")
        print("OK")
    except Exception as e:
        print(f"FAIL: {e}")
        failures.append(("Enum validation", e))

    # --- 3. Client init + health check ---
    print("[3/6] Health check...", end=" ")
    try:
        client = RoExClient(api_key=api_key)
        health = client.health_check()
        print(f"OK ({health})")
    except Exception as e:
        print(f"FAIL: {e}")
        failures.append(("Health check", e))
        print("\nCannot reach API. Remaining tests will likely fail.")

    # --- 4. Upload ---
    print("[4/6] File upload...", end=" ")
    audio_path = os.path.join(os.path.dirname(__file__), "fixtures", "audio", "test_track.wav")
    track_url = None
    try:
        if not os.path.exists(audio_path):
            print(f"SKIP (no fixture at {audio_path})")
        else:
            track_url = upload_file(client, audio_path)
            assert track_url and track_url.startswith("http")
            print(f"OK ({track_url[:60]}...)")
    except Exception as e:
        print(f"FAIL: {e}")
        failures.append(("File upload", e))

    # --- 5. Analysis (uses updated AnalysisMusicalStyle) ---
    print("[5/6] Analysis...", end=" ")
    if not track_url:
        print("SKIP (no uploaded URL)")
    else:
        try:
            request = MixAnalysisRequest(
                audio_file_location=track_url,
                musical_style=AnalysisMusicalStyle.POP,
                is_master=False,
            )
            results = client.analysis.analyze_mix(request)
            assert results is not None
            print(f"OK (keys: {list(results.keys()) if isinstance(results, dict) else 'non-dict'})")
        except Exception as e:
            print(f"FAIL: {e}")
            failures.append(("Analysis", e))

    # --- 6. Enhance preview (uses updated EnhanceMusicalStyle + payload) ---
    print("[6/6] Enhance preview...", end=" ")
    if not track_url:
        print("SKIP (no uploaded URL)")
    else:
        try:
            enhance_req = MixEnhanceRequest(
                audio_file_location=track_url,
                musical_style=EnhanceMusicalStyle.POP,
                is_master=False,
            )
            task = client.enhance.create_mix_enhance_preview(enhance_req)
            assert task.mixrevive_task_id is not None
            assert task.error is False
            print(f"OK (task_id: {task.mixrevive_task_id})")
        except Exception as e:
            print(f"FAIL: {e}")
            failures.append(("Enhance preview", e))

    # --- Summary ---
    print("\n" + "=" * 50)
    if failures:
        print(f"SMOKE TEST: {len(failures)} FAILURE(S)")
        for name, err in failures:
            print(f"  - {name}: {err}")
        sys.exit(1)
    else:
        print("SMOKE TEST: ALL PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
