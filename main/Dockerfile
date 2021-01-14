FROM python:3.7-slim-buster
ENV http_proxy http://10.0.0.7:8866
ENV https_proxy http://10.0.0.7:8866

RUN apt-get update
RUN apt-get install -y build-essential curl python3-smbus 
WORKDIR /app/

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /

ARG INSTALL_DEV=true
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

COPY . /app/
ENV PYTHONPATH=/
ENV PYTHONUNBUFFERED=0