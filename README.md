# Flux.1 on Vast.ai

A simple HTTP API server for Flux.1 image generation, optimized for GPU instances on Vast.ai.

## Features

- 🚀 Fast inference with FLUX.1-schnell (4 steps, ~45 seconds)
- 🔗 UUID-based image URLs
- 📡 RESTful HTTP API with async job queue
- 💾 Optimized for 8GB VRAM (RTX 3070/3080/etc)
- 🔄 Sequential CPU offloading for memory efficiency
- ✅ Health check and status endpoints

## Quick Start

### On Vast.ai

1. Launch a GPU instance with:
   - **GPU:** 8GB+ VRAM (RTX 3070, 3080, etc.)
   - **Image:** PyTorch CUDA template or Ubuntu with CUDA
   - **Disk:** 30GB+ (for models)

2. Clone and setup:
```bash
git clone https://github.com/brandynette/flux1-vast-ai.git
cd flux1-vast-ai
pip install -r requirements.txt
```

3. Set your HuggingFace token:
```bash
export HF_TOKEN='your_hf_token_here'
```

4. Start the server:
```bash
python3 server.py
```

Server will be available on port 5000.

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Authenticate with HuggingFace
export HF_TOKEN='your_token'

# Start server
python3 server.py
```

## API Usage

### Generate Image

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a cat wearing sunglasses", "steps": 4}'
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_url": "/status/550e8400-e29b-41d4-a716-446655440000",
  "image_url": "/image/550e8400-e29b-41d4-a716-446655440000"
}
```

### Check Status

```bash
curl http://localhost:5000/status/<job_id>
```

### Download Image

```bash
curl http://localhost:5000/image/<job_id> -o output.png
```

## CLI Tool

```bash
python3 flux_inference.py --prompt "a futuristic city" --output city.png
```

## Performance

- **Model:** FLUX.1-schnell
- **GPU:** RTX 3070 (8GB VRAM)
- **Generation time:** ~45 seconds (4 steps, 1024x1024)
- **First run:** ~5 minutes (model download ~17GB)

See [SERVER_README.md](SERVER_README.md) for full API documentation.
