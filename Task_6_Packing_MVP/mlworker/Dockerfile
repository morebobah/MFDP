FROM python:3.12-slim-bookworm
WORKDIR /app
COPY ./requirements.txt /app/
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
CMD ["python", "worker.py"]

