# Use Python 3.9 base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY model.py \
     register_model.py \
     requirements.txt \
     /app/

# Install necessary Python packages
RUN pip install -r requirements.txt

# Copy the entrypoint script
COPY serve_model.sh /serve_model.sh

# Make sure the script is executable
RUN chmod +x /serve_model.sh

# Set the entrypoint script
ENTRYPOINT ["/serve_model.sh"]