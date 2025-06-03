FROM python:3.13

RUN apt-get update && apt-get install -y curl postgresql-client && apt-get clean

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000

CMD ["python3 manage.py migrate"]
CMD ["python3 manage.py filldb"]
CMD ["gunicorn", "flashcards.wsgi:application", "--bind", "0.0.0.0:8000"]
