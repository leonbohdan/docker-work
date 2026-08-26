FROM python:3.12.14

WORKDIR /app

COPY app.py .
COPY docker-logo.jpg .

RUN pip install Flask

EXPOSE 8080

ENTRYPOINT [ "python", "app.py" ]
