FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

ENV PYTHONUNBUFFERED=1 \
  POETRY_HOME="/opt/poetry" \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  BUILD_PATH="/opt/build" \
  PYSETUP_PATH="/opt/project" \
  VENV_PATH="/opt/project/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY ./pyproject.toml /app/

RUN poetry install --without dev

COPY ./app /app