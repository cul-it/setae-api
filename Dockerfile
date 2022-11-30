FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
  cd /usr/local/bin && \
  ln -s /opt/poetry/bin/poetry && \
  poetry config virtualenvs.create false

COPY ./pyproject.toml /app/

RUN poetry install --no-dev

COPY ./app /app

# Send print & log statements directly to stdout
ENV PYTHONUNBUFFERED 1
