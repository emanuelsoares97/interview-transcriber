# interview transcriber

## para que serve

Transcreve em tempo real o que dizes ao microfone e/ou o que está a tocar no pc (tipo áudio de reunião, vídeo, etc). backend em flask + whisper, frontend em javascript puro. simples e direto.

Meu objetivo foi criar algo que podesse ajudar em entrevistas, reuniões.. em inglês.

Uso de IA no projeto, principalmente no frontend, e no processo de audios.

---

## estrutura do projeto

```
repo-root/
  apps/
    backend/    
      app.py                # arranca tudo, rotas e eventos
      audio_processing.py   # trata do áudio do mic
      system_audio_worker.py# trata do áudio do pc
      config.py             # configs fáceis de mudar
      requirements.txt
    frontend/   # javascript puro
  readme.md
```

---

## como correr isto

```bash
git clone ...
cd interview-transcriber
python -m venv .venv && source .venv/bin/activate
pip install -r apps/backend/requirements.txt
cd apps/backend
python app.py
# abre http://localhost:5000 no browser para usar o frontend
```


## sobre áudio do sistema (windows, linux, macos)

### microfone
- funciona em qualquer sistema, sem stress.

### áudio do pc (o que ouves)
- windows:
  - o windows não deixa gravar o áudio do pc direto.
  - para isso, instala [vb-audio cable](https://vb-audio.com/cable/) ou [voicemeeter](https://vb-audio.com/voicemeeter/).
  - depois de instalar, mete o "cable input" como saída padrão do windows ou da app.
  - no backend, grava do "cable output".
  - para ouvires nos fones, ativa "escutar este dispositivo" nas propriedades do "cable output".

  #### passo a passo vb-audio cable (windows)
  1. instala o vb-audio cable e reinicia o pc.
  2. vai ao painel de controlo de som > separador "reprodução".
  3. mete o **CABLE Input (VB-Audio Virtual Cable)** como dispositivo predefinido.
  4. vai ao separador "gravação", seleciona **CABLE Output**, clica em propriedades.
  5. no separador "escutar", ativa **escutar este dispositivo** e escolhe os teus fones/headset.
  6. clica em ok. agora ouves tudo nos fones e podes gravar o áudio do pc escolhendo o "cable output" no programa.
  7. o microfone continua a funcionar normalmente.
  8. se quiseres gravar mic + sistema ao mesmo tempo, precisas de misturar (ex: voicemeeter).


se não quiseres instalar nada, só funciona o microfone.

---

## dicas rápidas
- o backend agora está dividido por ficheiros, cada um faz uma coisa (olha os comentários nos .py)
- se não encontrar o dispositivo de áudio, avisa no frontend/backend o que falta.
- podes escolher o dispositivo por variável de ambiente ou no config.py.
- se quiseres mudar o modelo whisper, é só trocar no config.py (tiny, base, small, etc)

---

## problemas comuns
- system audio não aparece:
  - instala e configura o dispositivo virtual.
  - testa com `ffmpeg -list_devices true -f dshow -i dummy` (windows) para ver se aparece "cable output".
- só apanha o mic:
  - windows não deixa gravar o áudio do pc sem virtual cable.
- erro de permissão:
  - corre o terminal como admin.

---

## queres contribuir
- pr e issues são bem-vindos
- licença mit

---

## links úteis
- [whisper (openai)](https://github.com/openai/whisper)
- [vb-audio cable](https://vb-audio.com/cable/)
- [voicemeeter](https://vb-audio.com/voicemeeter/)
