FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

#RUN python manage.py collectstatic --noinput

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]