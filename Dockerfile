FROM python:3.10-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src

# Expose ports
EXPOSE 7860 3021

# Set environment variables
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV GRADIO_SERVER_PORT="7860"
ENV PYTHONPATH="/app/src"

# Make startup script executable
RUN chmod +x src/start_services.sh

# Run both services
CMD ["/bin/bash", "src/start_services.sh"]
