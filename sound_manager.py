import os
import shutil
import subprocess
import threading
import queue

# Maps DroneEngage 2-letter language codes (as sent by jsc_ctrl_audio.jsx /
# js_commands_api.js API_soundTextToSpeech) to espeak-ng voice names. Keep this
# in sync with the language dropdown in jsc_ctrl_audio.jsx.
LANGUAGE_MAP = {
    'ar': 'ar',
    'en': 'en-us',
    'ru': 'ru',
    'es': 'es',
    'ja': 'ja',
}

# Bounded so a burst of TTS/play requests can't pile up unbounded memory/latency.
# When full, the oldest queued item is dropped in favor of the newest one.
MAX_QUEUE_SIZE = 5


def build_sound_list(config):
    """
    Extracts the configured sound file library from the module config dict and
    returns it in the compact payload form sent to the GCS via
    TYPE_AndruavMessage_SOUND_LIST: a list of {"n": name, "f": file_path}.
    Entries missing a name or file path are skipped.
    """
    files = config.get('sound_files') if isinstance(config, dict) else None
    if not isinstance(files, list):
        return []
    result = []
    for entry in files:
        if not isinstance(entry, dict):
            continue
        name = entry.get('name')
        file_path = entry.get('file')
        if name and file_path:
            result.append({"n": name, "f": file_path})
    return result


class CSoundManager(object):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CSoundManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Guard against re-initialization: CSoundManager() is called every time a
        # message is parsed (singleton pattern), and without this guard __init__
        # would silently reset volume/pitch/language/mute back to defaults on
        # every single incoming message.
        if getattr(self, '_initialized', False):
            return
        self._initialized = True

        self.m_volume = 100          # 0-100 scale (as received from the databus)
        self.m_pitch = 50            # espeak-ng pitch range: 0-99
        self.m_language = 'en-us'    # espeak-ng voice name
        self.m_muted = False

        # Optional callback(description: str) invoked when playback/speech fails.
        # Wired by the module's main script to report errors back over the databus.
        self.m_on_error = None

        self._queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def configure(self, default_volume=None, default_pitch=None, default_language=None, muted=None):
        """
        Applies default settings, e.g. read from the module's config file at
        startup, or re-applied live after a remote CONFIG_ACTION_APPLY_CONFIG.
        """
        if isinstance(default_volume, int):
            self.m_volume = max(0, min(default_volume, 100))
        if isinstance(default_pitch, int):
            self.m_pitch = max(0, min(default_pitch, 99))
        if isinstance(default_language, str):
            self.m_language = LANGUAGE_MAP.get(default_language, self.m_language)
        if muted is not None:
            self.m_muted = bool(muted)

    def set_muted(self, muted):
        self.m_muted = bool(muted)

    # ------------------------------------------------------------------
    # Public API - both are non-blocking: they enqueue work for the
    # background worker thread so the UDP receive/parse thread never
    # blocks waiting for espeak-ng/aplay to finish.
    # ------------------------------------------------------------------

    def say(self, text, language=None, pitch=None, volume=None):
        if self.m_muted or not text:
            return

        voice = LANGUAGE_MAP.get(language, self.m_language) if language else self.m_language
        actual_pitch = pitch if isinstance(pitch, int) else self.m_pitch
        actual_volume = volume if isinstance(volume, int) else self.m_volume

        actual_pitch = max(0, min(actual_pitch, 99))
        amplitude = max(0, min(actual_volume, 100)) * 2  # espeak-ng "-a" range is 0-200

        self._enqueue(('say', text, voice, actual_pitch, amplitude))

    def play_file(self, file_path):
        if self.m_muted or not file_path:
            return

        self._enqueue(('play', file_path))

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _enqueue(self, item):
        try:
            self._queue.put_nowait(item)
        except queue.Full:
            # Drop the oldest queued item to make room for the newest request.
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self._queue.put_nowait(item)
            except queue.Full:
                self._report_error("Sound queue full, dropping request")

    def _worker_loop(self):
        while True:
            item = self._queue.get()
            try:
                if item[0] == 'say':
                    _, text, voice, pitch, amplitude = item
                    self._say_sync(text, voice, pitch, amplitude)
                elif item[0] == 'play':
                    _, file_path = item
                    self._play_file_sync(file_path)
            except subprocess.CalledProcessError as e:
                self._report_error(f"Sound command failed: {e}")
            except FileNotFoundError as e:
                self._report_error(f"Sound backend not found: {e}")
            except Exception as e:
                self._report_error(f"Unexpected sound error: {e}")

    def _say_sync(self, text, voice, pitch, amplitude):
        subprocess.run(
            ["espeak-ng", "-a", str(amplitude), "-v", voice, "-p", str(pitch), text],
            check=True
        )

    def _play_file_sync(self, file_path):
        if not os.path.isfile(file_path):
            self._report_error(f"Sound file not found: {file_path}")
            return

        player = self._pick_player(file_path)
        if player is None:
            self._report_error(f"No suitable audio player found for: {file_path}")
            return

        subprocess.run(player + [file_path], check=True)

    def _pick_player(self, file_path):
        """
        Picks an available command-line audio player based on file extension.
        Prefers tools that are already installed on most Debian/RPi images
        (alsa-utils' aplay) so file playback works out of the box wherever
        espeak-ng is already present, without requiring new dependencies.
        """
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.wav' and shutil.which("aplay"):
            return ["aplay", "-q"]
        if ext == '.mp3' and shutil.which("mpg123"):
            return ["mpg123", "-q"]
        if shutil.which("ffplay"):
            return ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"]
        if ext == '.wav' and shutil.which("aplay"):
            return ["aplay", "-q"]

        return None

    def _report_error(self, description):
        print(f"ERROR: {description}")
        if self.m_on_error:
            try:
                self.m_on_error(description)
            except Exception as e:
                print(f"ERROR: on_error callback failed: {e}")
