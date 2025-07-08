# Interview Transcriber (Monorepo)

## Pra que serve?

Transcreve em tempo real o que você fala no microfone **e/ou** o que está rolando no PC (tipo áudio de reunião, vídeo, etc). Backend em Flask + Whisper, frontend em JS puro. Simples e direto.

---

## Estrutura do projeto

```
repo-root/
  apps/
    backend/    # Flask + Socket.IO
    frontend/   # JS puro
  packages/     # utilidades compartilhadas
  docker/       # Docker e compose
  .env.example  # exemplo de variáveis
  README.md     # este arquivo
```

---

## Como rodar rapidão

```bash
git clone ...
cd interview-transcriber
python -m venv .venv && source .venv/bin/activate
pip install -r apps/backend/requirements.txt
cp .env.example .env  # se precisar
python apps/backend/main.py  # backend
# Abre http://localhost:5000 no navegador pra usar o frontend
```

Se preferir Docker:

```bash
docker compose up --build
```

---

## Sobre áudio do sistema (Windows, Linux, macOS)

### Microfone
- Funciona em qualquer sistema, sem stress.

### Áudio do PC (o que você ouve)
- **Windows:**
  - O Windows não deixa capturar o áudio do PC direto.
  - Pra isso, tem que instalar [VB-Audio Cable](https://vb-audio.com/Cable/) ou [VoiceMeeter](https://vb-audio.com/Voicemeeter/).
  - Depois de instalar, coloca o "CABLE Input" como saída padrão do Windows ou do app.
  - No backend, grava do "CABLE Output".
  - Pra ouvir nos fones, ativa "Escutar este dispositivo" nas propriedades do "CABLE Output".
- **Linux:**
  - Usa PulseAudio/ALSA. Procura por "Monitor of ..." nos dispositivos de gravação.
- **macOS:**
  - Usa [BlackHole](https://existential.audio/blackhole/) ou [Loopback](https://rogueamoeba.com/loopback/).

Se não quiser instalar nada, só vai funcionar o microfone mesmo.

---

## Dicas rápidas
- O backend tenta achar o dispositivo certo sozinho.
- Se não achar, vai avisar no frontend/backend o que falta.
- Dá pra escolher o dispositivo por variável de ambiente/config.

---

## Problemas comuns
- **System audio não aparece:**
  - Instala e configura o dispositivo virtual.
  - Testa com `ffmpeg -list_devices true -f dshow -i dummy` (Windows) pra ver se aparece "CABLE Output".
- **Só pega o mic:**
  - Windows não libera o áudio do PC sem virtual cable.
- **Erro de permissão:**
  - Roda o terminal como admin.
- **Docker não pega áudio:**
  - Roda local pra testar áudio.

---

## Privacidade
- O app pode gravar qualquer áudio do PC e do mic.
- Use com responsabilidade.

---

## Quer contribuir?
- PR e issues são bem-vindos!
- Licença MIT.

---

## Exemplo

![Exemplo de uso](docs/demo.gif)

---

## Links úteis
- [Whisper (OpenAI)](https://github.com/openai/whisper)
- [VB-Audio Cable](https://vb-audio.com/Cable/)
- [VoiceMeeter](https://vb-audio.com/Voicemeeter/)
- [BlackHole (macOS)](https://existential.audio/blackhole/)
