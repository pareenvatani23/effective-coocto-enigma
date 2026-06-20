# Voice Cloning PoC — container image.
#
# Build:  docker build -t voice-clone-poc .
# Run:    docker run --rm -p 7860:7860 voice-clone-poc
#         then open http://localhost:7860
#
# Notes:
# - First synthesis downloads model weights from Hugging Face, so the container
#   needs outbound access to huggingface.co at runtime.
# - CPU works (slower); for GPU, base this on an nvidia/cuda image and install
#   the CUDA build of torch.
FROM python:3.11-slim

# System libs: libsndfile for soundfile, ffmpeg for audio decode/encode.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libsndfile1 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install deps first so the layer caches across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cache model weights inside the image's working area at runtime.
ENV HF_HOME=/app/.cache/huggingface \
    GRADIO_PORT=7860

EXPOSE 7860

# The app binds 0.0.0.0 and reads GRADIO_PORT / GRADIO_SHARE / GRADIO_AUTH.
CMD ["python", "app.py"]
