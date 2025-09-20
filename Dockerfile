FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg libsamplerate0-dev

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p raw_videos splitted_audios

COPY main.py .

CMD ["python", "main.py"]
