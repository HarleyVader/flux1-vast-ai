# Quick Start Guide

## 🚀 One-Command Setup

```bash
# 1. Clone repository
git clone https://github.com/HarleyVader/flux1-vast-ai.git && cd flux1-vast-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your HuggingFace token
export HF_TOKEN='your_hf_token_here'

# 4. Start server
nohup python3 server.py > server.log 2>&1 &

# 5. Get your public URL
echo "Your API is at: http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"
```

## 📡 Access Your Server

Find your public URL:
```bash
echo "http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"
```

## 🎨 Generate Your First Image

```bash
# Replace with your actual public URL
curl -X POST http://YOUR_IP:YOUR_PORT/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "a beautiful mountain landscape", "steps": 4}'
```

This returns a `job_id`. View your image at:
```
http://YOUR_IP:YOUR_PORT/image/<job_id>
```

## ✅ Verify Installation

```bash
# Check server health
curl http://localhost:6006/health

# View logs
tail -f server.log
```

## 🛠️ Configuration Files

- `server.py` - Main HTTP server
- `flux_inference.py` - CLI tool
- `requirements.txt` - Python dependencies
- `VAST_AI_SETUP.md` - Full deployment guide

## 📖 Full Documentation

See [VAST_AI_SETUP.md](VAST_AI_SETUP.md) for complete deployment guide.

## ⚡ Performance

- **GPU:** RTX 3070 (8GB)
- **Generation Time:** ~40-45 seconds
- **Resolution:** 1024x1024
- **First Run:** ~5 minutes (model download)

## 🔒 Security Note

This is a basic setup. For production:
- Add authentication
- Use HTTPS
- Implement rate limiting
- Monitor for abuse
