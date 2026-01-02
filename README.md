# Flux.1 on Vast.ai

A complete HTTP API server for Flux.1 image generation, optimized for GPU instances on Vast.ai with UUID-based image URLs.

## Features

- 🚀 Fast inference with FLUX.1-schnell (4 steps, ~40 seconds)
- 🔗 UUID-based image URLs for easy sharing
- 📡 RESTful HTTP API with async job queue
- 💾 Optimized for 8GB VRAM (RTX 3070/3080/etc)
- 🔄 Sequential CPU offloading for memory efficiency
- ✅ Health check and status endpoints
- 🌐 Public internet access via Vast.ai port mapping

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for one-command setup.

### On Vast.ai (Recommended)

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
./start.sh
# Or manually:
nohup python3 server.py > server.log 2>&1 &
```

5. Get your public URL:
```bash
echo "http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"
```

### Full Setup Guide

See [VAST_AI_SETUP.md](VAST_AI_SETUP.md) for complete deployment instructions.

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - One-command setup guide
- **[VAST_AI_SETUP.md](VAST_AI_SETUP.md)** - Complete Vast.ai deployment guide  
- **[SERVER_README.md](SERVER_README.md)** - API documentation
- **[ENVIRONMENT.md](ENVIRONMENT.md)** - Configuration reference

## File Structure

```
flux1-vast-ai/
├── server.py              # HTTP API server (runs on port 6006)
├── flux_inference.py      # CLI inference tool
├── start.sh              # Auto-start script
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── QUICKSTART.md        # Quick setup guide
├── VAST_AI_SETUP.md    # Full deployment guide
├── SERVER_README.md     # API documentation
└── ENVIRONMENT.md       # Configuration reference
```

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
- **Generation time:** ~40-45 seconds (4 steps, 1024x1024)
- **First run:** ~5 minutes (model download ~17GB)
- **Memory:** Optimized for 8GB VRAM with CPU offloading

## Tested Configuration

- **GPU:** NVIDIA GeForce RTX 3070 (8GB)
- **CUDA:** 12.1.1
- **Driver:** 535.230.02
- **Platform:** Vast.ai
- **Public IP:** Accessible worldwide

See [SERVER_README.md](SERVER_README.md) for full API documentation.
