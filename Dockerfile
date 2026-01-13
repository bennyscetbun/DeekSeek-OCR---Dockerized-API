# DeepSeek-OCR vLLM Docker Image
# Based on official vLLM OpenAI image for better compatibility

FROM debian:bookworm-slim
# Set the default command to use our custom server
# Override the entrypoint to run our script directly
# Use the full path to python to avoid PATH issues
ENTRYPOINT ["/usr/bin/python3", "/app/start_server.py"]
