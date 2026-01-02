# Flux.1 HTTP Server

Simple HTTP API for Flux.1 image generation with UUID-based URLs.

## Quick Start

```bash
# Start the server
export HF_TOKEN='your_hf_token_here'
python3 server.py
```

Server runs on `http://0.0.0.0:5000`

## API Endpoints

### Generate Image
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a cat wearing sunglasses"}'
```

Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status_url": "/status/550e8400-e29b-41d4-a716-446655440000",
  "image_url": "/image/550e8400-e29b-41d4-a716-446655440000"
}
```

### Check Status
```bash
curl http://localhost:5000/status/550e8400-e29b-41d4-a716-446655440000
```

### Download Image
```bash
curl http://localhost:5000/image/550e8400-e29b-41d4-a716-446655440000 -o output.png
# OR open in browser:
# http://localhost:5000/image/550e8400-e29b-41d4-a716-446655440000
```

### Health Check
```bash
curl http://localhost:5000/health
```

## Full Example

```bash
# Generate image
JOB=$(curl -s -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a futuristic city at sunset", "steps": 4}' | jq -r '.job_id')

# Check status
curl http://localhost:5000/status/$JOB

# Download when ready
curl http://localhost:5000/image/$JOB -o my_image.png
```

## Request Parameters

- `prompt` (required): Text description
- `steps` (optional): Number of steps (default: 4)
- `width` (optional): Image width (default: 1024)
- `height` (optional): Image height (default: 1024)
- `seed` (optional): Random seed for reproducibility

## Features

- ✅ Async job queue (non-blocking)
- ✅ UUID-based image URLs
- ✅ Status tracking (pending/processing/complete/error)
- ✅ Thread-safe model access
- ✅ Automatic memory optimization
- ✅ Health check endpoint
