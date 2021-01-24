FROM python:latest

USER root

WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD python3 api.py