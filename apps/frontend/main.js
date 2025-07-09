// socket para falar com o backend (websocket)
const socket = io({ transports: ['websocket'] });
// apanha os elementos do html
const mixedTranscript = document.getElementById('mixedTranscript');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const startSystemBtn = document.getElementById('startSystemBtn');
const stopSystemBtn = document.getElementById('stopSystemBtn');
const clearBtn = document.getElementById('clearBtn');
const socketStatus = document.getElementById('socketStatus');
const lastEvent = document.getElementById('lastEvent');

let mediaRecorder;
let stream;
let recordingInterval = false;

// mete texto na caixa de transcrições (mic ou system)
function appendTranscript(text, type) {
  const p = document.createElement('p');
  p.textContent = (type === 'mic' ? '[mic] ' : '[system] ') + text;
  p.className = type === 'mic' ? 'transcript-mic' : 'transcript-system';
  if (!text || text.trim() === '' || text.trim() === '(vazio)') {
    p.className = 'transcript-empty';
  } else if (text.startsWith('Erro na transcrição')) {
    p.className = 'transcript-error';
  }
  mixedTranscript.appendChild(p);
  mixedTranscript.scrollTop = mixedTranscript.scrollHeight;
}

// mostra se o socket está ligado ou não
function updateSocketStatus() {
  socketStatus.textContent = 'socket: ' + (socket.connected ? 'ligado' : 'desligado');
  console.log('[frontend] Estado do socket:', socket.connected);
}

updateSocketStatus();
socket.on('connect', () => { updateSocketStatus(); console.log('[frontend] Ligado ao backend'); });
socket.on('disconnect', () => { updateSocketStatus(); console.log('[frontend] Desligado do backend'); });

// mostra o último evento recebido
function setLastEvent(ev) {
  lastEvent.textContent = 'último evento: ' + ev;
  console.log('[frontend] Evento recebido:', ev);
}

// quando chega transcrição do mic
socket.on('transcript', (data) => {
  setLastEvent('transcript');
  appendTranscript(data.text, 'mic');
  console.log('[frontend] Recebido transcript:', data.text);
});

// quando chega transcrição do sistema
socket.on('system_transcript', (data) => {
  setLastEvent('system_transcript');
  appendTranscript(data.text, 'system');
  console.log('[frontend] Recebido system_transcript:', data.text);
});

// começa a gravar o mic em ciclos de 3 segundos
async function startRecordingCycle() {
  try {
    if (!stream) {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      console.log('[frontend] Obtido stream do microfone');
    }
    mediaRecorder = new MediaRecorder(stream);
    let chunks = [];

    mediaRecorder.ondataavailable = e => {
      if (e.data.size > 0) {
        chunks.push(e.data);
      }
    };

    mediaRecorder.onstop = async () => {
      try {
        if (chunks.length > 0) {
          const blob = new Blob(chunks, { type: 'audio/webm' });
          const reader = new FileReader();
          reader.onload = function() {
            const base64data = reader.result.split(',')[1];
            socket.emit('audio_chunk', base64data);
            console.log('[frontend] Enviando audio_chunk');
          };
          reader.readAsDataURL(blob);
          chunks = [];
        }
        // se ainda está a gravar, começa novo ciclo
        if (recordingInterval) {
          setTimeout(() => {
            console.log('[frontend] Novo ciclo de gravação');
            startRecordingCycle();
          }, 10);
        }
      } catch (err) {
        appendTranscript('Erro no onstop do MediaRecorder: ' + err, 'mic');
        console.error('[frontend] Erro no onstop do MediaRecorder:', err);
      }
    };

    mediaRecorder.start();
    setTimeout(() => {
      if (mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
    }, 3000); // 3 segundos
    console.log('[frontend] Iniciado ciclo de gravação do mic');
  } catch (err) {
    appendTranscript('Erro no ciclo de gravação: ' + err, 'mic');
    console.error('[frontend] Erro no ciclo de gravação:', err);
  }
}

// botões do mic
startBtn.onclick = async () => {
  console.log('[frontend] Clicado iniciar mic');
  startBtn.disabled = true;
  stopBtn.disabled = false;
  recordingInterval = true;
  await startRecordingCycle();
};

stopBtn.onclick = () => {
  console.log('[frontend] Clicado parar mic');
  startBtn.disabled = false;
  stopBtn.disabled = true;
  recordingInterval = false;
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
};

// botões do sistema (áudio do pc)
startSystemBtn.onclick = () => {
  console.log('[frontend] Clicado iniciar system');
  socket.emit('start_system_audio');
  startSystemBtn.disabled = true;
  stopSystemBtn.disabled = false;
};

stopSystemBtn.onclick = () => {
  console.log('[frontend] Clicado parar system');
  socket.emit('stop_system_audio');
  setTimeout(() => {
    console.log('[frontend] Estado do socket após emitir stop_system_audio:', socket.connected);
  }, 500);
  startSystemBtn.disabled = false;
  stopSystemBtn.disabled = true;
};

// botão limpar
clearBtn.onclick = () => {
  console.log('[frontend] Clicado limpar');
  mixedTranscript.innerHTML = '';
};

// se o socket cair, desativa botões
socket.on('disconnect', () => {
  startSystemBtn.disabled = false;
  stopSystemBtn.disabled = true;
  startBtn.disabled = false;
  stopBtn.disabled = true;
}); 