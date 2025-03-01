FROM python:3.7

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /usr/src/app/src

CMD ["python", "server.py"]
