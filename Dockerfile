FROM python:3.9.13

WORKDIR ./rayoj-server

ADD . .

RUN pip install -r requirements.txt

CMD ["python", "./src/main.py"]