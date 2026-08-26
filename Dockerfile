ARG PYTHON_VERSION=3.12.14

FROM python:${PYTHON_VERSION}

ENV MY_ENV_VAR=development

WORKDIR /app

COPY app.py .
COPY docker-logo.jpg .

RUN pip install Flask

EXPOSE 8080

ENTRYPOINT [ "python", "app.py" ]
