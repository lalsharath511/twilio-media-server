# vad_utils.py
from webrtcvad import Vad

def is_human_voice(audio_bytes, sample_rate=16000):
    vad = Vad(2)
    frame_duration = 30
    frame_length = int(sample_rate * frame_duration / 1000) * 2

    for i in range(0, len(audio_bytes) - frame_length, frame_length):
        chunk = audio_bytes[i:i + frame_length]
        if vad.is_speech(chunk, sample_rate):
            return True
    return False