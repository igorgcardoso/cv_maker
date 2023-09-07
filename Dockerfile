FROM python:3.11.1-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV production

RUN apt-get update && apt-get install -y libgtk2.0-0

COPY requirements.txt .

RUN pip install --upgrade pip && \
  pip install -r requirements.txt

COPY . .

WORKDIR /app/src

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "cv_maker.wsgi:application"]
