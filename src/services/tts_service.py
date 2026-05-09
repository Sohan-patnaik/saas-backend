# tts_service.py
import os
import base64
import requests
from flask import current_app
from flask_limiter.util import get_remote_address

# Load ElevenLabs config from environment
ELEVEN_API_KEY = os.getenv("ELEVENLABS_API_KEY")
VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
ELEVEN_MODEL_ID = "eleven_multilingual_v2"
ELEVEN_TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

# Per-IP cache: {ip: {text: base64_audio}}
tts_cache_per_ip: dict[str, dict[str, str]] = {}


def tts_generate_mp3(text: str,
                     voice_settings: dict | None = None,
                     timeout: int = 30) -> bytes:
    """Call ElevenLabs TTS REST API and return MP3 bytes."""
    payload = {"text": text, "model_id": ELEVEN_MODEL_ID}
    if voice_settings:
        payload["voice_settings"] = voice_settings
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_API_KEY
    }

    try:
        resp = requests.post(ELEVEN_TTS_URL, json=payload, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.content
        else:
            current_app.logger.error("ElevenLabs TTS failed: %s %s", resp.status_code, resp.text)
            return b""
    except requests.RequestException as e:
        current_app.logger.error("ElevenLabs TTS request exception: %s", e)
        return b""


def get_tts_audio(bot_reply: str, user_ip: str) -> str | None:
    """Return base64 audio for bot_reply, caching per user_ip."""
    if user_ip not in tts_cache_per_ip:
        tts_cache_per_ip[user_ip] = {}

    if bot_reply in tts_cache_per_ip[user_ip]:
        return tts_cache_per_ip[user_ip][bot_reply]

    audio_bytes = tts_generate_mp3(bot_reply)
    if audio_bytes:
        b64 = base64.b64encode(audio_bytes).decode("ascii")
        audio_data_uri = f"data:audio/mpeg;base64,{b64}"
        tts_cache_per_ip[user_ip][bot_reply] = audio_data_uri
        return audio_data_uri
    return None
