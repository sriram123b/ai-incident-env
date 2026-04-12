# Use lightweight Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn requests

# Expose port (HF uses 7860)
EXPOSE 7860

# Run the app
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]