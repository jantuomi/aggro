FROM python:3.11-alpine

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY app ./app
COPY plugins ./plugins
COPY aggro.py ./aggro.py

CMD ["python", "aggro.py"]
