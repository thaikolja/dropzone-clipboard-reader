import os
import subprocess
import time


class AudioPlaybackError(Exception):
    """Raised when audio playback fails."""


def play_audio(file_path, progress_callback=None):
    """Play an audio file with optional progress reporting.

    Uses ``afinfo`` to determine the estimated duration of the file,
    then plays it via ``afplay``. If a progress callback is supplied
    the function polls playback progress every 100 ms and reports it
    as a percentage from 0 to 99. The file is always deleted after
    playback finishes (or if playback fails).

    Args:
        file_path: Absolute path to the audio file on disk.
        progress_callback: Optional callable that accepts an integer
            percentage (0--99) and is invoked periodically during playback.

    Raises:
        AudioPlaybackError: If afplay fails or the file cannot be played.
    """
    try:
        _play_and_cleanup(file_path, progress_callback)
    finally:
        _cleanup_file(file_path)


def _cleanup_file(file_path):
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except OSError:
        pass


def _get_duration(file_path):
    """Get the estimated duration in seconds from afinfo."""
    try:
        output = subprocess.check_output(
            ["afinfo", file_path], text=True, stderr=subprocess.DEVNULL
        )
        for line in output.splitlines():
            if "estimated duration" in line:
                return float(line.split(":")[-1].strip().split()[0])
    except Exception:
        pass
    return None


def _play_and_cleanup(file_path, progress_callback):
    duration = _get_duration(file_path)

    if duration and duration > 0 and progress_callback:
        proc = subprocess.Popen(["afplay", file_path])
        start = time.time()

        while proc.poll() is None:
            elapsed = time.time() - start
            percent = min(int((elapsed / duration) * 100), 99)
            try:
                progress_callback(percent)
            except Exception:
                pass
            time.sleep(0.1)

        ret = proc.wait()
        if ret != 0:
            raise AudioPlaybackError(
                f"afplay exited with code {ret}"
            )
    else:
        result = subprocess.run(["afplay", file_path])
        if result.returncode != 0:
            raise AudioPlaybackError(
                f"afplay exited with code {result.returncode}"
            )

    if progress_callback:
        try:
            progress_callback(99)
        except Exception:
            pass
