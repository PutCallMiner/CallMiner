# Use Python 3.10 base image
FROM python:3.10-slim

# Set the working directory in the container
RUN apt update \
    && apt install -y ffmpeg \
    && apt install -y cython3 \
    && apt install -y git \
    && apt install -y g++ \
    && pip install Cython 

WORKDIR /app

# Install necessary Python packages
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy relevant Python code into the container at /app
COPY model.py \
    register_model.py \
    whisper_nemo_diarization.py \
    /app/

# Copy the entrypoint script
COPY serve_model.sh /serve_model.sh

# Make sure the script is executable
RUN chmod +x /serve_model.sh

# Set the entrypoint script
ENTRYPOINT [ "/serve_model.sh" ]