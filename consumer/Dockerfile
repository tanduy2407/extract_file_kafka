FROM python:3.10.8
WORKDIR /app
COPY requirements.txt .
COPY consumer.py .
RUN mkdir file
RUN pip install -r requirements.txt
CMD [ "python" , "consumer.py" ]