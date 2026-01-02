# Vast.ai Deployment Guide for Flux.1

Complete step-by-step guide to deploy the Flux.1 HTTP API server on Vast.ai.

## Prerequisites

- Vast.ai account (https://vast.ai)
- HuggingFace account with Flux.1 access
- HuggingFace token with Read permissions

## Step 1: Get HuggingFace Token

1. Go to https://huggingface.co/join and create an account
2. Accept the FLUX.1-schnell license at https://huggingface.co/black-forest-labs/FLUX.1-schnell
3. Create a token at https://huggingface.co/settings/tokens
   - Choose **"Read"** access
   - Copy the token (starts with `hf_...`)

## Step 2: Launch Vast.ai Instance

### Recommended Specifications:

```
GPU:          RTX 3070 / 3080 / 4070 or better (8GB+ VRAM)
Disk Space:   30GB minimum (for models)
Image:        PyTorch with CUDA 12.x
Bandwidth:    Unmetered preferred
```

### Launch Command:

1. Go to https://vast.ai/console/create/
2. Search for instances with:
   - **GPU RAM:** >= 8 GB
   - **Disk Space:** >= 30 GB
   - **GPU Model:** RTX 3070, 3080, 4070, etc.

3. Select an instance and click **"Rent"**

4. In the setup screen:
   - **Image:** Select `pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime` or similar
   - **Jupyter:** Optional (can disable)
   - Click **"Create"**

## Step 3: Connect to Instance

### Via SSH:

```bash
ssh -p PORT root@IP_ADDRESS
# Port and IP shown in Vast.ai console
```

### Via Web Terminal:

Click **"Terminal"** button in Vast.ai console

## Step 4: Install and Setup

### Clone Repository:

```bash
cd /workspace
git clone https://github.com/HarleyVader/flux1-vast-ai.git
cd flux1-vast-ai
```

### Install Dependencies:

```bash
pip install -r requirements.txt
```

### Set HuggingFace Token:

```bash
export HF_TOKEN='your_hf_token_here'
# Or for permanent:
echo "export HF_TOKEN='your_hf_token_here'" >> ~/.bashrc
```

## Step 5: Start the Server

### Run in Background:

```bash
nohup python3 server.py > server.log 2>&1 &
```

### Check Status:

```bash
tail -f server.log
# Press Ctrl+C to stop viewing
```

### Verify Server is Running:

```bash
curl http://localhost:6006/health
```

Should return:
```json
{
  "gpu": "NVIDIA GeForce RTX 3070",
  "model_loaded": true,
  "status": "healthy"
}
```

## Step 6: Access Publicly

### Find Your Public URL:

1. Check environment variables:
```bash
echo "Public IP: $PUBLIC_IPADDR"
echo "Port mapping for 6006: $VAST_TCP_PORT_6006"
```

2. Your public URL will be:
```
http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006
```

**Example:** `http://94.239.253.223:49483`

### Test Public Access:

```bash
# From your local machine:
curl http://YOUR_PUBLIC_IP:PORT/health
```

## Step 7: Generate Images

### Via Command Line:

```bash
# Generate image
curl -X POST http://YOUR_PUBLIC_IP:PORT/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "a beautiful sunset", "steps": 4}'

# Returns job_id, then access at:
# http://YOUR_PUBLIC_IP:PORT/image/<job_id>
```

### Via Browser:

1. Open: `http://YOUR_PUBLIC_IP:PORT/`
2. See API documentation
3. Generate images by POSTing to `/generate`
4. View images at `/image/<job_id>`

## Port Mapping Reference

Vast.ai maps internal ports to external ports. Common mappings:

| Internal Port | External Port (varies) | Purpose |
|---------------|------------------------|---------|
| 22 | VAST_TCP_PORT_22 | SSH |
| 6006 | VAST_TCP_PORT_6006 | **Flux.1 API** |
| 8080 | VAST_TCP_PORT_8080 | Jupyter |
| 8384 | VAST_TCP_PORT_8384 | Syncthing |

**Check your mappings:**
```bash
env | grep VAST_TCP_PORT
```

## Configuration Details

### Server Configuration:

- **Port:** 6006 (internal)
- **Host:** 0.0.0.0 (all interfaces)
- **Model:** FLUX.1-schnell
- **Memory:** Optimized for 8GB VRAM

### Optimizations Applied:

- Sequential CPU offloading
- VAE slicing
- VAE tiling
- bfloat16 precision

## Troubleshooting

### 1. Out of Memory Error

**Solution:**
```bash
# Reduce image resolution in request
{
  "prompt": "...",
  "width": 768,
  "height": 768
}
```

### 2. Port Not Accessible

**Check:**
```bash
# Verify server is running
ps aux | grep "python3 server.py"

# Check port binding
netstat -tulpn | grep 6006

# Verify firewall (usually not needed on Vast.ai)
```

### 3. Model Download Slow

First run downloads ~17GB of models. This can take 5-10 minutes depending on bandwidth.

**Monitor:**
```bash
tail -f server.log
```

### 4. Authentication Error

**Solution:**
```bash
# Verify token is set
echo $HF_TOKEN

# Re-login
huggingface-cli login
```

### 5. Server Stops After Disconnect

**Use screen or tmux:**
```bash
# Install screen
apt-get update && apt-get install -y screen

# Start in screen
screen -S flux
python3 server.py
# Press Ctrl+A then D to detach

# Reattach later
screen -r flux
```

## Performance Metrics

### Test Configuration:
- **GPU:** RTX 3070 (8GB VRAM)
- **Resolution:** 1024x1024
- **Steps:** 4
- **Generation Time:** ~40-45 seconds

### Memory Usage:
- **Model Loading:** ~7.5 GB VRAM
- **Inference:** ~7.8 GB VRAM (peak)
- **CPU Offloading:** Keeps usage under 8GB

## API Quick Reference

### Generate Image:
```bash
POST /generate
{
  "prompt": "text description",
  "steps": 4,           # optional, default 4
  "width": 1024,        # optional, default 1024
  "height": 1024,       # optional, default 1024
  "seed": 42            # optional, for reproducibility
}
```

### Check Status:
```bash
GET /status/<job_id>
```

### Get Image:
```bash
GET /image/<job_id>
```

### Health Check:
```bash
GET /health
```

## Cost Optimization

### Tips to Minimize Costs:

1. **Stop instance when not in use** - Vast.ai charges by the hour
2. **Use spot instances** - Cheaper but can be interrupted
3. **Choose slower GPUs** - RTX 3060 works fine for testing
4. **Monitor usage** - Set up alerts in Vast.ai dashboard

### Estimated Costs (as of 2026):

- RTX 3070: ~$0.20-0.40/hour
- RTX 3080: ~$0.30-0.60/hour
- RTX 4070: ~$0.40-0.80/hour

## Security Considerations

### Best Practices:

1. **Don't commit tokens to git**
2. **Use environment variables for secrets**
3. **Consider adding API key authentication** (not included by default)
4. **Monitor for abuse** if exposed publicly
5. **Set up rate limiting** for production use

### Optional: Add Basic Auth

Edit `server.py` and add:
```python
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'admin' and password == 'your_password'

def authenticate():
    return Response('Authentication required', 401,
                   {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Then add @requires_auth to endpoints
@app.route('/generate', methods=['POST'])
@requires_auth
def generate():
    ...
```

## Maintenance

### Update Code:

```bash
cd /workspace/flux1-vast-ai
git pull
pip install -r requirements.txt --upgrade
# Restart server
```

### View Logs:

```bash
tail -f /workspace/flux1-vast-ai/server.log
```

### Clear Generated Images:

```bash
rm -rf /workspace/flux1-vast-ai/outputs/*
```

## Support

- **GitHub Issues:** https://github.com/HarleyVader/flux1-vast-ai/issues
- **Vast.ai Support:** https://vast.ai/console/support
- **HuggingFace:** https://huggingface.co/black-forest-labs/FLUX.1-schnell

## License

This project uses FLUX.1-schnell which has its own license terms.
See: https://huggingface.co/black-forest-labs/FLUX.1-schnell
