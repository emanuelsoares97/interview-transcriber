import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import base64
import tempfile
import whisper
import os
import re
import subprocess
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

# Worker para capturar e transcrever áudio do sistema
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Carregar modelo Whisper uma vez
whisper_model = whisper.load_model('tiny')

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

last_transcript = {'mic': None, 'system': None}

# Configuração: ativar filtro de transcrições?
FILTER_TRANSCRIPTS = True  # Altere para False para desativar o filtro

# --- Controle do worker de áudio do sistema ---
system_audio_thread = None
system_audio_stop_event = threading.Event()

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

@app.route('/emit_test')
def emit_test():
    socketio.emit('transcript', {'text': 'TESTE_BACKEND_EVENTO'})
    return {'status': 'ok', 'msg': 'Evento transcript emitido'}

@app.route('/emit_system_test')
def emit_system_test():
    socketio.emit('system_transcript', {'text': 'TESTE SYSTEM AUDIO'})
    return {'status': 'ok', 'msg': 'system_transcript emitido'}

@socketio.on('connect')
def handle_connect():
    print(f'[backend] Cliente conectado: {request.sid}')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'[backend] Cliente desconectado: {request.sid}')

# Evento para receber áudio do frontend
@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    try:
        sid = request.sid
        print(f'\033[94m[backend] Recebido audio_chunk de {sid}\033[0m')
        # Se vier como DataURL, remova o prefixo
        if isinstance(data, str) and data.startswith('data:'):
            data = re.sub('^data:audio/\\w+;base64,', '', data)
        audio_bytes = base64.b64decode(data)
        # Salvar como webm
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmpfile:
            tmpfile.write(audio_bytes)
            tmpfile_path = tmpfile.name
        # Converter para WAV
        wav_fd, wav_path = tempfile.mkstemp(suffix='.wav')
        os.close(wav_fd)
        try:
            ffmpeg_cmd = [
                'ffmpeg', '-y', '-i', tmpfile_path,
                '-ar', '16000', '-ac', '1', '-f', 'wav', wav_path
            ]
            result_ffmpeg = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[audio_chunk] FFmpeg stderr:", result_ffmpeg.stderr.decode())
            # Transcrever com Whisper
            try:
                result = whisper_model.transcribe(wav_path, fp16=False, language='en')
                transcript_text = result.get('text', '').strip()
                print(f"\033[92m[audio_chunk] Transcrição: {transcript_text}\033[0m")
            except Exception as e:
                transcript_text = f'Erro na transcrição: {e}'
                print(f"\033[91m[audio_chunk] Erro na transcrição: {e}\033[0m")
            # Filtro simples
            if FILTER_TRANSCRIPTS:
                if (not transcript_text or not transcript_text.strip() or
                    transcript_text.startswith('Erro na transcrição') or
                    transcript_text == last_transcript['mic']):
                    print(f'\033[93m[backend] Ignorado (vazio, erro ou repetido)\033[0m')
                else:
                    print(f'\033[96m[backend] Emitindo transcript para {sid}: {transcript_text}\033[0m')
                    socketio.emit('transcript', {'text': transcript_text}, to=sid)
                    last_transcript['mic'] = transcript_text
            else:
                print(f'\033[96m[backend] Emitindo transcript para {sid}: {transcript_text}\033[0m')
                socketio.emit('transcript', {'text': transcript_text}, to=sid)
                last_transcript['mic'] = transcript_text
        finally:
            # Limpeza garantida
            try:
                os.remove(tmpfile_path)
            except Exception as e:
                print(f'\033[91m[backend] Erro ao remover tmpfile_path: {e}\033[0m')
            try:
                os.remove(wav_path)
            except Exception as e:
                print(f'\033[91m[backend] Erro ao remover wav_path: {e}\033[0m')
    except Exception as e:
        print('\033[91mErro ao processar audio_chunk:\033[0m', e)

def system_audio_worker():
    duration = 3  # segundos
    while not system_audio_stop_event.is_set():
        try:
            print('[system_audio_worker] Capturando áudio do sistema via ffmpeg/DShow...')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
                tmpfile_path = tmpfile.name
            # Comando ffmpeg para capturar apenas o áudio do PC (VB-Cable via DirectShow)
            # Se o nome do dispositivo for diferente, ajusta aqui:
            ffmpeg_cmd = [
                'ffmpeg',
                '-y',
                '-f', 'dshow',
                '-i', 'audio=CABLE Output (VB-Audio Virtual Cable)',
                '-t', str(duration),
                '-ar', '16000', '-ac', '1', '-f', 'wav', tmpfile_path
            ]
            result_ffmpeg = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("[system_audio_worker] FFmpeg stderr:", result_ffmpeg.stderr.decode())
            # Transcrever
            try:
                result = whisper_model.transcribe(tmpfile_path, fp16=False, language='en')
                transcript_text = result.get('text', '').strip()
                print(f'[system_audio_worker] Transcrição: {transcript_text}')
            except Exception as e:
                transcript_text = f'Erro na transcrição: {e}'
                print(f'[system_audio_worker] Erro: {e}')
            os.remove(tmpfile_path)
            # Filtro simples para system audio
            if FILTER_TRANSCRIPTS:
                if (not transcript_text or not transcript_text.strip() or
                    transcript_text.startswith('Erro na transcrição') or
                    transcript_text == last_transcript['system']):
                    print(f'\033[93m[backend] Ignorado system (vazio, erro ou repetido)\033[0m')
                else:
                    print(f'\033[96m[backend] Emitindo system_transcript: {transcript_text}\033[0m')
                    with app.app_context():
                        socketio.emit('system_transcript', {'text': transcript_text})
                    last_transcript['system'] = transcript_text
            else:
                print(f'\033[96m[backend] Emitindo system_transcript: {transcript_text}\033[0m')
                with app.app_context():
                    socketio.emit('system_transcript', {'text': transcript_text})
                last_transcript['system'] = transcript_text
        except Exception as e:
            print('[system_audio_worker] Erro geral:', e)
        import time; time.sleep(2)
    print('[system_audio_worker] Parando worker de áudio do sistema.')

@socketio.on('start_system_audio')
def start_system_audio():
    print('[backend] RECEBIDO start_system_audio')
    global system_audio_thread
    if system_audio_thread and system_audio_thread.is_alive():
        print('[backend] system_audio_worker já está rodando.')
        return
    print('[backend] Iniciando system_audio_worker...')
    system_audio_stop_event.clear()
    system_audio_thread = socketio.start_background_task(system_audio_worker)

@socketio.on('stop_system_audio')
def stop_system_audio():
    print('[backend] RECEBIDO stop_system_audio')
    print('[backend] Parando system_audio_worker...')
    system_audio_stop_event.set()

if __name__ == '__main__':
    import eventlet
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=True)