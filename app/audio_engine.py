from gtts import gTTS
from io import BytesIO

class AudioEngine:
    def __init__(self):
        self._cache = {}

    def get_audio_bytes(self, text: str, lang: str = "zh-CN") -> bytes:
        if text in self._cache:
            return self._cache[text]

        mp3_fp = BytesIO()
        tts = gTTS(text=text, lang=lang)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        audio_bytes = mp3_fp.read()
        self._cache[text] = audio_bytes
        return audio_bytes
