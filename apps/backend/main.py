from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import eventlet
import base64
import tempfile
import whisper
import os
import re

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Carregar modelo Whisper uma vez
whisper_model = whisper.load_model('base')

@app.route('/')
def index():
    return jsonify({'message': 'Backend Flask rodando!'})

# Evento para receber áudio do frontend
@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    try:
        # Se vier como DataURL, remova o prefixo
        if isinstance(data, str) and data.startswith('data:'):
            data = re.sub('^data:audio/\\w+;base64,', '', data)
        audio_bytes = base64.b64decode(data)
        # Salvar como arquivo temporário WEBM
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmpfile:
            tmpfile.write(audio_bytes)
            tmpfile_path = tmpfile.name
        # Transcrever com Whisper
        result = whisper_model.transcribe(tmpfile_path, fp16=False, language='pt')
        transcript_text = result.get('text', '').strip()
        # Limpar arquivo temporário
        os.remove(tmpfile_path)
        # Enviar transcrição real para o frontend
        emit('transcript', {'text': transcript_text or '(vazio)'}, broadcast=False)
    except Exception as e:
        print('Erro na transcrição:', e)
        emit('transcript', {'text': f'Erro na transcrição: {e}'}, broadcast=False)

if __name__ == '__main__':
    # Usar eventlet para WebSocket
    socketio.run(app, debug=True, host='0.0.0.0')