import eventlet
# isto tem de vir mesmo no topo, senão dá erro
# serve para o flask e socketio funcionarem juntos

eventlet.monkey_patch()

import threading
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from config import FRONTEND_DIR, FILTER_TRANSCRIPTS
from audio_processing import process_audio_chunk
from system_audio_worker import system_audio_worker


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# para guardar a última transcrição (mic e sistema)
last_transcript = {'mic': None, 'system': None}

# controlo do worker do áudio do sistema
app.system_audio_thread = None
app.system_audio_stop_event = threading.Event()

# rota principal, serve o frontend
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIR, 'index.html')

# serve ficheiros estáticos do frontend
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# rota só para testar se o backend está a emitir eventos
@app.route('/emit_test')
def emit_test():
    socketio.emit('transcript', {'text': 'TESTE_BACKEND_EVENTO'})
    return {'status': 'ok', 'msg': 'Evento transcript emitido'}

# rota para testar evento do sistema
@app.route('/emit_system_test')
def emit_system_test():
    socketio.emit('system_transcript', {'text': 'TESTE SYSTEM AUDIO'})
    return {'status': 'ok', 'msg': 'system_transcript emitido'}

# quando alguém liga ao socket
@socketio.on('connect')
def handle_connect():
    print(f'[backend] Cliente conectado: {request.sid}')

# quando alguém desliga do socket
@socketio.on('disconnect')
def handle_disconnect():
    print(f'[backend] Cliente desconectado: {request.sid}')

# recebe áudio do frontend (mic)
@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    try:
        sid = request.sid
        print(f'\033[94m[backend] Recebido audio_chunk de {sid}\033[0m')
        transcript_text = process_audio_chunk(data, language='en')
        # só manda para o frontend se não for vazio, erro ou repetido
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
    except Exception as e:
        print('\033[91mErro ao processar audio_chunk:\033[0m', e)

# começa a escuta do áudio do sistema
@socketio.on('start_system_audio')
def start_system_audio():
    print('[backend] RECEBIDO start_system_audio')
    if app.system_audio_thread and app.system_audio_thread.is_alive():
        print('[backend] system_audio_worker já está rodando.')
        return
    print('[backend] Iniciando system_audio_worker...')
    app.system_audio_stop_event.clear()
    app.system_audio_thread = socketio.start_background_task(system_audio_worker, socketio, app)

# para o worker do áudio do sistema
@socketio.on('stop_system_audio')
def stop_system_audio():
    print('[backend] RECEBIDO stop_system_audio')
    print('[backend] Parando system_audio_worker...')
    app.system_audio_stop_event.set()

# aqui é onde se arranca tudo
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=True) 