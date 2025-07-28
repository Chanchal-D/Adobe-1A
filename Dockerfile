FROM --platform=linux/amd64 python:3.10
WORKDIR /app
COPY src/main.py /app/
COPY requirements.txt /app/
RUN pip install -r requirements.txt
CMD ["python", "main.py"]