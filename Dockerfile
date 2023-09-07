FROM python:3.11.1-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV production

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-dev --no-root

COPY . .

WORKDIR /app/src

EXPOSE 8000

CMD ["gunicorn" "-b", "0.0.0.0:8000", "cv_maker.wsgi:application"]
