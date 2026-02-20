FROM python:3.11-slim
WORKDIR /app

COPY ./libs ./libs
COPY ./requirements.docker.txt .
RUN pip install --no-cache-dir -r requirements.docker.txt

COPY ./src ./src
COPY ./config ./config
COPY ./main.py .
CMD sleep 0.5 && python main.py