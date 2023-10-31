# Use Python 3.10.8 as the base image
FROM python:3.10.8

# Set the working directory inside the container
WORKDIR /app

# Copy requirements.txt and consumer.py into the container
COPY requirements.txt .
COPY consumer.py .

# Create a directory named 'file' inside the container
RUN mkdir file

# Create the offset.txt file with the value '0' inside the container
RUN echo "0" > offset.txt

# Install Python dependencies
RUN pip install -r requirements.txt

# CMD to run the consumer.py script
CMD ["python", "consumer.py"]
