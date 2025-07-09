import base64
import tempfile
import subprocess
import os
import re
import whisper
from config import WHISPER_MODEL_SIZE

# carrega o modelo whisper só uma vez (pode demorar um bocadinho)
whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)

# função para tratar o áudio que vem do frontend (mic)
def process_audio_chunk(data, language='en'):
    # se vier como dataurl, tira o prefixo
    if isinstance(data, str) and data.startswith('data:'):
        data = re.sub(r'^data:audio/\w+;base64,', '', data)
    audio_bytes = base64.b64decode(data)
    # guarda como webm temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmpfile:
        tmpfile.write(audio_bytes)
        tmpfile_path = tmpfile.name
    # converte para wav (whisper só aceita wav)
    wav_fd, wav_path = tempfile.mkstemp(suffix='.wav')
    os.close(wav_fd)
    try:
        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', tmpfile_path,
            '-ar', '16000', '-ac', '1', '-f', 'wav', wav_path
        ]
        result_ffmpeg = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("[audio_processing] FFmpeg stderr:", result_ffmpeg.stderr.decode())
        # tenta transcrever com whisper
        try:
            result = whisper_model.transcribe(wav_path, fp16=False, language=language)
            transcript_text = result.get('text', '').strip()
            print(f"[audio_processing] Transcrição: {transcript_text}")
        except Exception as e:
            transcript_text = f'Erro na transcrição: {e}'
            print(f"[audio_processing] Erro na transcrição: {e}")
        return transcript_text
    finally:
        # apaga os ficheiros temporários (limpeza)
        try:
            os.remove(tmpfile_path)
        except Exception as e:
            print(f'[audio_processing] Erro ao remover tmpfile_path: {e}')
        try:
            os.remove(wav_path)
        except Exception as e:
            print(f'[audio_processing] Erro ao remover wav_path: {e}') 