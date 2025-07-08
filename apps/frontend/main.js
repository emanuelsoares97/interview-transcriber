window.onload = function() {
  try {
    console.log('[frontend] DOM loaded, inicializando...');
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const transcript = document.getElementById('transcript');
    const clearBtn = document.getElementById('clearBtn');
    const systemTranscript = document.getElementById('systemTranscript');
    const micStatus = document.getElementById('micStatus');
    const exportBtn = document.getElementById('exportBtn');
    const recordingIndicator = document.getElementById('recordingIndicator');
    const startSystemBtn = document.getElementById('startSystemBtn');
    const stopSystemBtn = document.getElementById('stopSystemBtn');

    // Conexão com backend Flask-SocketIO
    const socket = io('http://localhost:5000');

    // Log de conexão WebSocket
    socket.on('connect', () => {
      console.log('[frontend] Conectado ao backend via WebSocket');
    });
    socket.on('disconnect', () => {
      console.warn('[frontend] Desconectado do backend WebSocket');
    });
    socket.on('reconnect', () => {
      console.log('[frontend] Reconectado ao backend WebSocket');
    });
    socket.onAny((event, data) => {
      console.log(`[frontend] Evento recebido: ${event}`, data);
    });
    // Log de status dos elementos DOM
    function logDomStatus() {
      console.log('[frontend] transcript:', transcript);
      console.log('[frontend] systemTranscript:', systemTranscript);
      console.log('[frontend] micStatus:', micStatus);
      console.log('[frontend] recordingIndicator:', recordingIndicator);
    }
    logDomStatus();

    function createTranscriptElement(text, lastText) {
      const p = document.createElement('p');
      p.textContent = text;
      if (!text || text.trim() === '' || text.trim() === '(vazio)') {
          p.className = 'transcript-empty';
      } else if (text === lastText) {
          p.className = 'transcript-repeat';
      } else if (text.startsWith('Erro na transcrição')) {
          p.className = 'transcript-error';
      } else {
          p.className = 'transcript-normal';
      }
      return p;
  }
  

    let lastMicText = null;
    let lastSystemText = null;
    let micEmptyCount = 0;
    let systemEmptyCount = 0;

    function appendOrGroupEmpty(parent, emptyCount, type) {
      if (emptyCount > 1) {
        const p = document.createElement('p');
        p.className = 'transcript-empty-group';
        p.textContent = `... [${type} vazios x${emptyCount}] ...`;
        parent.appendChild(p);
        parent.scrollTop = parent.scrollHeight;
      }
    }

    // Função para scroll automático suave
    function smoothScrollToBottom(element) {
      element.scrollTo({ top: element.scrollHeight, behavior: 'smooth' });
    }

    // Função para exportar transcrições em TXT
    exportBtn.onclick = () => {
      let txt = 'Microphone Transcript:\n';
      transcript.querySelectorAll('p, .transcript-empty-group').forEach(p => {
        txt += p.textContent + '\n';
      });
      txt += '\nSystem Audio Transcript:\n';
      systemTranscript.querySelectorAll('p, .transcript-empty-group').forEach(p => {
        txt += p.textContent + '\n';
      });
      const blob = new Blob([txt], { type: 'text/plain' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'transcricoes.txt';
      a.click();
    };

    socket.on('transcript', (data) => {
      console.log('[frontend] Recebido transcript:', data.text);
      if (!data.text || data.text.trim() === '' || data.text.trim() === '(vazio)') {
        micEmptyCount++;
        if (micStatus) {
          micStatus.style.display = 'block';
        }
      } else {
        appendOrGroupEmpty(transcript, micEmptyCount, 'mic');
        micEmptyCount = 0;
        if (micStatus) micStatus.style.display = 'none';
        const p = createTranscriptElement(data.text, lastMicText);
        if (transcript) {
          transcript.appendChild(p);
          smoothScrollToBottom(transcript);
        } else {
          console.error('[frontend] transcript element not found!');
        }
        lastMicText = data.text;
      }
    });

    socket.on('system_transcript', (data) => {
      console.log('[frontend] Recebido system_transcript:', data.text);
      if (!data.text || data.text.trim() === '' || data.text.trim() === '(vazio)') {
        systemEmptyCount++;
      } else {
        appendOrGroupEmpty(systemTranscript, systemEmptyCount, 'system');
        systemEmptyCount = 0;
        const p = createTranscriptElement(data.text, lastSystemText);
        if (systemTranscript) {
          systemTranscript.appendChild(p);
          smoothScrollToBottom(systemTranscript);
        } else {
          console.error('[frontend] systemTranscript element not found!');
        }
        lastSystemText = data.text;
      }
    });

    let mediaRecorder;
    let stream;
    let recordingInterval = false;

    async function startRecordingCycle() {
      try {
        if (!stream) {
          stream = await navigator.mediaDevices.getUserMedia({ audio: true });
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
                console.log('[frontend] Enviando audio_chunk');
                socket.emit('audio_chunk', base64data);
              };
              reader.readAsDataURL(blob);
              chunks = [];
            }
            if (recordingInterval) {
              setTimeout(() => {
                console.log('[frontend] Novo ciclo de gravação');
                startRecordingCycle();
              }, 10);
            }
          } catch (err) {
            console.error('[frontend] Erro no onstop do MediaRecorder:', err);
          }
        };

        mediaRecorder.start();
        setTimeout(() => {
          if (mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
          }
        }, 2000);
      } catch (err) {
        console.error('[frontend] Erro no ciclo de gravação:', err);
      }
    }

    startBtn.onclick = async () => {
      startBtn.disabled = true;
      stopBtn.disabled = false;
      recordingInterval = true;
      if (recordingIndicator) recordingIndicator.style.display = 'flex';
      await startRecordingCycle();
    };

    stopBtn.onclick = () => {
      startBtn.disabled = false;
      stopBtn.disabled = true;
      recordingInterval = false;
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
      if (recordingIndicator) recordingIndicator.style.display = 'none';
    };

    clearBtn.onclick = () => {
      transcript.innerHTML = '';
      systemTranscript.innerHTML = '';
      micEmptyCount = 0;
      systemEmptyCount = 0;
      if (micStatus) micStatus.style.display = 'none';
      if (recordingIndicator) recordingIndicator.style.display = 'none';
    };

    // Controle dos botões de system audio
    startSystemBtn.onclick = () => {
      console.log('[frontend] Solicitando início do system audio ao backend');
      socket.emit('start_system_audio');
      startSystemBtn.disabled = true;
      stopSystemBtn.disabled = false;
    };
    stopSystemBtn.onclick = () => {
      console.log('[frontend] Solicitando parada do system audio ao backend');
      socket.emit('stop_system_audio');
      startSystemBtn.disabled = false;
      stopSystemBtn.disabled = true;
    };
    // Ao desconectar, resetar botões
    socket.on('disconnect', () => {
      startSystemBtn.disabled = false;
      stopSystemBtn.disabled = true;
    });
  } catch (err) {
    console.error('[frontend] Erro global:', err);
  }
};
window.addEventListener('error', function(e) {
  console.error('[frontend] Erro não capturado:', e.error || e.message);
}); 
window.addEventListener('unhandledrejection', function(e) {
  console.error('[frontend] Promise rejeitada não capturada:', e.reason);
}); 