FROM python:3.11-slim

# X-Topo Arg
ARG ENABLE_SVE
ARG ENABLE_SME

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# Environment defaults
ENV BACKEND_URL=http://llama-server:8080
ENV MAX_TOKENS=2048
ENV UI_TITLE="Arm CPU LLM Chat"
ENV ENABLE_SVE=${ENABLE_SVE}
ENV ENABLE_SME=${ENABLE_SME}

EXPOSE 3000

CMD ["python", "app.py"]
