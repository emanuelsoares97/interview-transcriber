# Interview Transcriber (Monorepo)

## O que é?

Transcrição em tempo real de entrevistas, reuniões ou qualquer áudio captado pelo microfone **e/ou** pelo sistema (áudio do PC), com backend Flask + Whisper e frontend em JavaScript puro.

---

## Estrutura

```
repo-root/
│
├── apps/
│   ├── backend/          # Flask + Socket.IO
│   └── frontend/         # JS puro
│
├── packages/             # Código compartilhado
│   └── common-utils/
│
├── docker/               # Dockerfiles e compose
│
├── .env.example          # Variáveis de ambiente modelo
└── README.md             # Este guia resumido
```

---

## Como rodar

```bash
git clone ...
cd interview-transcriber
python -m venv .venv && source .venv/bin/activate
pip install -r apps/backend/requirements.txt
cp .env.example .env  # adicione suas chaves
# Em terminais separados:
python apps/backend/main.py  # backend
# Acesse http://localhost:5000 para o frontend
```

Ou use Docker:

```bash
docker compose up --build
```

---

## ⚠️ Limitações e dicas para áudio do sistema (Windows, Linux, macOS)

### Microfone
- Funciona em qualquer sistema, sem configuração extra.

### Áudio do sistema (o que você ouve nos fones/alto-falantes)
- **Windows:**
  - O Windows NÃO expõe o áudio do sistema como input por padrão.
  - Para capturar, use um dispositivo virtual como [VB-Audio Cable (grátis)](https://vb-audio.com/Cable/) ou [VoiceMeeter](https://vb-audio.com/Voicemeeter/).
  - Após instalar, defina o "CABLE Input" como saída padrão do Windows ou do app de chamada.
  - No backend, selecione o dispositivo "CABLE Output" para gravação.
  - Para ouvir nos fones, ative "Escutar este dispositivo" nas propriedades do "CABLE Output".
- **Linux:**
  - Use PulseAudio/ALSA. Procure por "Monitor of ..." nos dispositivos de gravação.
- **macOS:**
  - Use [BlackHole](https://existential.audio/blackhole/) ou [Loopback](https://rogueamoeba.com/loopback/).

Se não quiser instalar nada, o app funcionará apenas com o microfone.

---

## Como escolher o dispositivo de áudio
- O backend tenta detectar dispositivos automaticamente.
- Se não encontrar, mostre uma mensagem amigável no frontend/backend explicando o que falta e como resolver.
- Permita que o usuário escolha o dispositivo de áudio via variável de ambiente ou configuração.

---

## Troubleshooting (Problemas comuns)
- **System audio não aparece:**
  - Verifique se o dispositivo virtual está instalado e configurado.
  - Teste com `ffmpeg -list_devices true -f dshow -i dummy` (Windows) para ver se aparece "CABLE Output".
- **Só capta o microfone:**
  - O Windows não expõe o áudio do sistema sem dispositivo virtual.
- **Erro de permissão:**
  - Execute o terminal como administrador.
- **Docker não acessa áudio:**
  - Prefira rodar localmente para testes de áudio.

---

## Privacidade e ética
- O app pode captar qualquer áudio do sistema e microfone.
- Use de forma responsável e respeite a privacidade de terceiros.

---

## Contribuição
- Pull requests e issues são bem-vindos!
- Veja o arquivo CONTRIBUTING.md para detalhes.
- Licença: MIT

---

## Prints e exemplos

![Exemplo de uso](docs/demo.gif)

---

## Referências
- [Whisper (OpenAI)](https://github.com/openai/whisper)
- [VB-Audio Cable](https://vb-audio.com/Cable/)
- [VoiceMeeter](https://vb-audio.com/Voicemeeter/)
- [BlackHole (macOS)](https://existential.audio/blackhole/)
