import os

# caminho para o frontend
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))
# se queres filtrar transcrições repetidas/vazias
FILTER_TRANSCRIPTS = True
# modelo whisper a usar (podes mudar para base, small, etc)
WHISPER_MODEL_SIZE = 'tiny'
# nome do dispositivo de áudio do sistema (windows)
SYSTEM_AUDIO_DEVICE = 'CABLE Output (VB-Audio Virtual Cable)'
# quanto tempo grava de cada vez (segundos)
SYSTEM_AUDIO_DURATION = 3  # segundos 