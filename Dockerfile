ARG PYTHON_VERSION=3.12.14

FROM python:${PYTHON_VERSION}

ENV MY_ENV_VAR=development

WORKDIR /app

ADD app.py .
ADD docker-logo.jpg .
ADD https://raw.githubusercontent.com/docker-library/docs/refs/heads/master/docker/README.md .

RUN pip install Flask

EXPOSE 8080

ENTRYPOINT [ "python", "app.py" ]
