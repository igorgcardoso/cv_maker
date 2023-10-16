FROM python:3.11.1-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV production

RUN apt-get update && apt-get install -y libgtk2.0-0

COPY requirements.txt .

RUN pip install --upgrade pip && \
  pip install -r requirements.txt

RUN ls
COPY /etc/secrets/.secrets.yaml .

COPY . .

RUN python src/manage.py migrate

WORKDIR /app/src

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "cv_maker.wsgi:application"]
