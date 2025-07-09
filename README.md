# interview transcriber (monorepo)

## para que serve

transcreve em tempo real o que dizes ao microfone e/ou o que está a tocar no pc (tipo áudio de reunião, vídeo, etc). backend em flask + whisper, frontend em javascript puro. simples e direto.

---

## estrutura do projeto

```
repo-root/
  apps/
    backend/    # flask + socket.io
    frontend/   # javascript puro
  packages/     # utilidades partilhadas
  docker/       # docker e compose
  .env.example  # exemplo de variáveis
  readme.md     # este ficheiro
```

---

## como correr isto

```bash
git clone ...
cd interview-transcriber
python -m venv .venv && source .venv/bin/activate
pip install -r apps/backend/requirements.txt
cp .env.example .env  # se precisares
python apps/backend/main.py  # backend
# abre http://localhost:5000 no browser para usar o frontend
```

se preferires docker:

```bash
docker compose up --build
```

---

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
- o backend tenta encontrar o dispositivo certo sozinho.
- se não encontrar, avisa no frontend/backend o que falta.
- podes escolher o dispositivo por variável de ambiente ou config.

---

## problemas comuns
- system audio não aparece:
  - instala e configura o dispositivo virtual.
  - testa com `ffmpeg -list_devices true -f dshow -i dummy` (windows) para ver se aparece "cable output".
- só apanha o mic:
  - windows não deixa gravar o áudio do pc sem virtual cable.
- erro de permissão:
  - corre o terminal como admin.
- docker não apanha áudio:
  - corre local para testar áudio.

---

## privacidade
- isto pode gravar qualquer áudio do pc e do mic.
- usa com responsabilidade.

---

## queres contribuir
- pr e issues são bem-vindos
- licença mit

---

## exemplo

![exemplo de uso](docs/demo.gif)

---

## links úteis
- [whisper (openai)](https://github.com/openai/whisper)
- [vb-audio cable](https://vb-audio.com/cable/)
- [voicemeeter](https://vb-audio.com/voicemeeter/)
- [blackhole (macos)](https://existential.audio/blackhole/)
