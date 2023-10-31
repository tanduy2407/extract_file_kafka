# Use Python 3.10.8 as the base image
FROM python:3.10.8

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and producer.py into the container
COPY requirements.txt .
COPY producer.py .

# Install Python dependencies
RUN pip install -r requirements.txt

# CMD to run the producer.py script
CMD [ "python" , "producer.py" ]