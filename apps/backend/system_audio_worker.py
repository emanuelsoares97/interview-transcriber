import tempfile
import subprocess
import os
import time
from config import SYSTEM_AUDIO_DEVICE, SYSTEM_AUDIO_DURATION, FILTER_TRANSCRIPTS
from audio_processing import whisper_model
from flask_socketio import SocketIO

# guarda a última transcrição do sistema
last_transcript = {'system': None}

# este worker corre em background e vai buscar o áudio do pc (tipo música, reunião, etc)
def system_audio_worker(socketio: SocketIO, app):
    while not app.system_audio_stop_event.is_set():
        try:
            print('[system_audio_worker] a gravar áudio do sistema...')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
                tmpfile_path = tmpfile.name
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',
                '-f', 'dshow',
                '-i', f'audio={SYSTEM_AUDIO_DEVICE}',
                '-t', str(SYSTEM_AUDIO_DURATION),
                '-ar', '16000', '-ac', '1', '-f', 'wav', tmpfile_path
            ]
            result_ffmpeg = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[system_audio_worker] FFmpeg stderr:", result_ffmpeg.stderr.decode())
            # tenta transcrever
            try:
                result = whisper_model.transcribe(tmpfile_path, fp16=False, language='en')
                transcript_text = result.get('text', '').strip()
                print(f'[system_audio_worker] transcrição: {transcript_text}')
            except Exception as e:
                transcript_text = f'Erro na transcrição: {e}'
                print(f'[system_audio_worker] erro: {e}')
            os.remove(tmpfile_path)
            # só manda se não for vazio, erro ou repetido
            if FILTER_TRANSCRIPTS:
                if (not transcript_text or not transcript_text.strip() or
                    transcript_text.startswith('Erro na transcrição') or
                    transcript_text == last_transcript['system']):
                    print(f'[system_audio_worker] ignorado (vazio, erro ou repetido)')
                else:
                    print(f'[system_audio_worker] a enviar system_transcript: {transcript_text}')
                    with app.app_context():
                        socketio.emit('system_transcript', {'text': transcript_text})
                    last_transcript['system'] = transcript_text
            else:
                print(f'[system_audio_worker] a enviar system_transcript: {transcript_text}')
                with app.app_context():
                    socketio.emit('system_transcript', {'text': transcript_text})
                last_transcript['system'] = transcript_text
        except Exception as e:
            print('[system_audio_worker] erro geral:', e)
        time.sleep(2)
    print('[system_audio_worker] a parar worker do sistema.') 