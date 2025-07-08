FROM python:3.10-slim

# Instalar ffmpeg e dependências do sistema
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ../../apps/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ../../apps/backend/ ./

# Baixar modelo Whisper base durante o build (opcional, acelera o primeiro uso)
RUN python -c "import whisper; whisper.load_model('base')"

CMD ["python", "main.py"] 