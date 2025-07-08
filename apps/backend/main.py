from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import eventlet
import base64
import tempfile
import whisper
import os
import re
import subprocess

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Carregar modelo Whisper uma vez
whisper_model = whisper.load_model('tiny')

@app.route('/')
def index():
    return jsonify({'message': 'Backend Flask rodando!'})

# Evento para receber áudio do frontend
@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    try:
        sid = request.sid
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
            print(f"[audio_chunk] Transcrição: {transcript_text}")
        except Exception as e:
            transcript_text = f'Erro na transcrição: {e}'
            print(f"[audio_chunk] Erro na transcrição: {e}")
        # Limpar arquivos temporários
        os.remove(tmpfile_path)
        os.remove(wav_path)
        # Enviar transcrição para o frontend
        socketio.emit('transcript', {'text': transcript_text or '(vazio)'}, room=sid)
    except Exception as e:
        print('Erro ao processar audio_chunk:', e)

if __name__ == '__main__':
    # Usar eventlet para WebSocket
    socketio.run(app, debug=True, host='0.0.0.0')