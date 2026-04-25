FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Python path
ENV PYTHONPATH=/app

# Port
ENV PORT=7860
EXPOSE 7860

# Run the agent GUI
CMD ["python", "diskova/agent/gui_chat.py"]