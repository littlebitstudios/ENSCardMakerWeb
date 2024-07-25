# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file into the container
COPY ./requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the font files into the container
COPY ./fonts ./fonts

# Copy the application code into the container
COPY ./ENSCardMakerWeb.py .

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application
CMD ["python", "ENSCardMakerWeb.py"]