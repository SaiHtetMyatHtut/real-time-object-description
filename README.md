https://onnxruntime.ai/docs/genai/tutorials/phi3-v.html

https://developer.nvidia.com/cudnn-downloads

# flash_attn
# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev

# Upgrade pip and install necessary Python packages
RUN pip install --upgrade pip setuptools wheel
RUN pip install packaging