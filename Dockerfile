# Base image from Hugging Face Spaces
FROM python:3.12-slim

# Install system dependencies and uv as root
RUN apt-get update && \
    apt-get install -y curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/ && \
    mv /root/.local/bin/uvx /usr/local/bin/ && \
    mkdir -p /.cache/uv

# Copy project configuration first
COPY pyproject.toml .  

# Install Python packages as root using uv sync
RUN uv sync && \
    rm -rf /.uv

# Create and switch to non-root user
RUN useradd -m -u 1000 user && \
    chown -R user:user /.cache/uv

USER user

# Set up environment
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:/usr/local/bin:$PATH \
    PORT=7860 \
    CHAINLIT_HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Copy application files with correct ownership
COPY --chown=user:user . .

# Expose the necessary ports
EXPOSE 8082
EXPOSE 7860

# Run the two required commands concurrently using bash process control
CMD ["bash", "-c", "uv run mcpdoc --yaml docs_config.yaml --transport sse --port 8082 --host localhost & uv run chainlit run src/axiom/app.py -h --port 7860 --host 0.0.0.0"]
