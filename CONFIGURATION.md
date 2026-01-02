# Configuration & Troubleshooting Guide

This document explains all the configuration steps taken to make the Flux.1 server accessible externally on Vast.ai, including problems encountered and solutions.

## Table of Contents

1. [Initial Setup Issues](#initial-setup-issues)
2. [Port Configuration](#port-configuration)
3. [Network Access Configuration](#network-access-configuration)
4. [Server Configuration](#server-configuration)
5. [Testing & Verification](#testing--verification)
6. [Common Issues & Solutions](#common-issues--solutions)

---

## Initial Setup Issues

### Problem 1: Server Running on Wrong Port

**Initial Configuration:**
```python
# server.py - WRONG
app.run(host='0.0.0.0', port=5000, debug=False)
```

**Issue:** Port 5000 is not mapped by Vast.ai to external access.

**Solution:** Use Vast.ai's port mapping system.

---

## Port Configuration

### Understanding Vast.ai Port Mapping

Vast.ai automatically maps certain internal ports to external ports for public access.

**Check Available Port Mappings:**
```bash
env | grep VAST_TCP_PORT
```

**Example Output:**
```
VAST_TCP_PORT_22=49577       # SSH
VAST_TCP_PORT_1111=49105     # Portal
VAST_TCP_PORT_6006=49483     # Available for custom use
VAST_TCP_PORT_8080=49600     # Jupyter
VAST_TCP_PORT_8384=49223     # Syncthing
```

### Choosing the Right Port

**Port 6006** is ideal because:
- It's typically used for TensorBoard (not running by default)
- Vast.ai maps it to an external port automatically
- No conflicts with existing services

**Final Configuration:**
```python
# server.py - CORRECT
app.run(host='0.0.0.0', port=6006, debug=False)
```

---

## Network Access Configuration

### Step 1: Verify Public IP

```bash
echo $PUBLIC_IPADDR
```

**Example:** `94.239.253.223`

### Step 2: Find External Port Mapping

```bash
echo $VAST_TCP_PORT_6006
```

**Example:** `49483`

### Step 3: Calculate Public URL

```bash
PUBLIC_URL="http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"
echo $PUBLIC_URL
```

**Example:** `http://94.239.253.223:49483`

---

## Server Configuration Journey

### Attempt 1: Port 5000 (Failed)

**Configuration:**
```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

**Result:** ❌ Server runs internally but not accessible externally.

**Why It Failed:** Port 5000 is not in Vast.ai's port mapping.

---

### Attempt 2: Port 80 with Caddy Reverse Proxy (Partial Success)

**Approach:** Use Caddy to proxy port 3000 to port 80.

**Configuration:**
```bash
# server.py
app.run(host='0.0.0.0', port=3000, debug=False)

# Caddyfile
:80 {
    reverse_proxy localhost:3000
}

# Start Caddy
caddy run --config /tmp/Caddyfile.flux --adapter caddyfile
```

**Result:** ❌ Works locally but external access blocked by Apache.

**Why It Failed:** Vast.ai's external port 80 routes through Apache, not directly to Caddy.

**Error Encountered:**
```html
HTTP/1.1 404 Not Found
Server: Apache/2.4.64 (Ubuntu)
```

---

### Attempt 3: Port 8080 (Failed)

**Configuration:**
```python
app.run(host='0.0.0.0', port=8080, debug=False)
```

**Result:** ❌ Port conflict with existing Jupyter service.

**Why It Failed:** Port 8080 already in use by Jupyter.

---

### Attempt 4: Port 6006 (Success!)

**Final Configuration:**
```python
# server.py - Line 232
app.run(host='0.0.0.0', port=6006, debug=False)
```

**Result:** ✅ Fully accessible externally!

**Why It Worked:**
- Port 6006 is automatically mapped by Vast.ai
- No conflicting services on this port
- Direct access without proxy needed
- Maps to external port via `$VAST_TCP_PORT_6006`

**Verification:**
```bash
# Local access
curl http://localhost:6006/health
{"gpu": "NVIDIA GeForce RTX 3070", "model_loaded": true, "status": "healthy"}

# External access
curl http://94.239.253.223:49483/health
{"gpu": "NVIDIA GeForce RTX 3070", "model_loaded": true, "status": "healthy"}
```

---

## Memory Optimization Configuration

### Problem: Out of Memory Error

**Initial Error:**
```
torch.OutOfMemoryError: CUDA out of memory. 
Tried to allocate 80.00 MiB. GPU 0 has 7.77 GiB memory in use.
```

**Initial Configuration (Failed):**
```python
pipe.enable_model_cpu_offload()  # WRONG - not aggressive enough
```

**Fixed Configuration:**
```python
pipe.enable_sequential_cpu_offload()  # CORRECT - sequential offloading
pipe.vae.enable_slicing()
pipe.vae.enable_tiling()
```

**Why It Matters:**
- `enable_model_cpu_offload()` keeps too much in VRAM
- `enable_sequential_cpu_offload()` moves models to CPU sequentially
- VAE slicing and tiling further reduce memory usage

**Result:** Successfully generates 1024x1024 images on 8GB VRAM!

---

## Testing & Verification

### Local Testing

```bash
# Test health endpoint
curl http://localhost:6006/health

# Expected output
{
  "gpu": "NVIDIA GeForce RTX 3070",
  "model_loaded": true,
  "status": "healthy"
}
```

### External Testing

```bash
# From your local machine or anywhere on internet
curl http://94.239.253.223:49483/health
```

### Full Integration Test

```bash
# 1. Generate image
RESPONSE=$(curl -s -X POST http://94.239.253.223:49483/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "a beautiful sunset", "steps": 4}')

# 2. Extract job ID
JOB_ID=$(echo $RESPONSE | jq -r '.job_id')
echo "Job ID: $JOB_ID"

# 3. Monitor status
while true; do
  STATUS=$(curl -s http://94.239.253.223:49483/status/$JOB_ID | jq -r '.status')
  echo "Status: $STATUS"
  [ "$STATUS" = "complete" ] && break
  sleep 5
done

# 4. Get image URL
echo "Image: http://94.239.253.223:49483/image/$JOB_ID"
```

---

## Common Issues & Solutions

### Issue 1: "Connection Refused" from External Access

**Symptoms:**
```bash
curl: (7) Failed to connect to IP port PORT: Connection refused
```

**Diagnosis:**
```bash
# 1. Check if server is running
ps aux | grep "python3 server.py"

# 2. Check if port is listening on all interfaces
netstat -tulpn | grep 6006
# Should show: 0.0.0.0:6006 (not 127.0.0.1:6006)

# 3. Verify port mapping exists
env | grep VAST_TCP_PORT_6006
```

**Solutions:**
1. Ensure server binds to `0.0.0.0` (not `127.0.0.1`)
2. Use correct external port from `$VAST_TCP_PORT_6006`
3. Restart server if needed

---

### Issue 2: "404 Not Found" from Public IP

**Symptoms:**
```html
HTTP/1.1 404 Not Found
Server: Apache/2.4.64 (Ubuntu)
<title>404 Not Found</title>
```

**Root Cause:** Trying to access port 80 instead of the mapped port.

**Wrong URL:**
```
http://94.239.253.223/health  ❌
```

**Correct URL:**
```
http://94.239.253.223:49483/health  ✅
```

**Solution:** Always use the external port from `$VAST_TCP_PORT_6006`.

---

### Issue 3: Server Stops After SSH Disconnect

**Symptoms:** Server terminates when SSH session closes.

**Solution:** Use `nohup`:

```bash
# Start with nohup
nohup python3 server.py > server.log 2>&1 &

# Server will persist after disconnect
```

**Verify it's running:**
```bash
ps aux | grep "python3 server.py"
tail -f server.log
```

---

### Issue 4: Out of Memory During Generation

**Symptoms:**
```
torch.cuda.OutOfMemoryError: CUDA out of memory
```

**Solutions:**

**1. Verify memory optimizations:**
```python
# In server.py - must use sequential, not model
pipe.enable_sequential_cpu_offload()  # ✅ Correct
# NOT: pipe.enable_model_cpu_offload()  ❌ Wrong

pipe.vae.enable_slicing()
pipe.vae.enable_tiling()
```

**2. Reduce image resolution:**
```json
{
  "prompt": "your prompt",
  "width": 768,
  "height": 768
}
```

**3. Check GPU usage:**
```bash
nvidia-smi

# If other processes are using GPU, stop them
kill <PID>
```

---

### Issue 5: HuggingFace Authentication Errors

**Symptoms:**
```
GatedRepoError: 401 Client Error. Cannot access gated repo
huggingface_hub.errors.GatedRepoError
```

**Root Cause:** Token not set or license not accepted.

**Solutions:**

**1. Set HF_TOKEN:**
```bash
export HF_TOKEN='hf_your_token_here'
echo $HF_TOKEN  # Verify it's set
```

**2. Accept model license:**
- Visit: https://huggingface.co/black-forest-labs/FLUX.1-schnell
- Click "Agree and access repository"

**3. Verify token permissions:**
- Go to: https://huggingface.co/settings/tokens
- Ensure token has "Read" access

---

### Issue 6: Slow First-Time Startup

**Symptoms:** Server appears to hang, no output for several minutes.

**What's Happening:** Downloading ~17GB of model files.

**Monitor Progress:**
```bash
tail -f server.log
```

**Example Output:**
```
transformer/diffusion_pytorch_model-0000(...): 15%|████▉ | 1.48G/9.95G [01:21<07:37, 18.5MB/s]
```

**Expected Time:**
- Fast connection (100+ Mbps): 3-5 minutes
- Medium connection (50 Mbps): 5-10 minutes
- Slow connection (10 Mbps): 10-15 minutes

**Verify Download Complete:**
```bash
# Check cache size (should be ~17GB)
du -sh ~/.cache/huggingface/
```

---

## Configuration Checklist

### ✅ Server Configuration
- [ ] Server runs on port 6006
- [ ] Server binds to 0.0.0.0 (not 127.0.0.1)
- [ ] Sequential CPU offloading enabled
- [ ] VAE slicing enabled
- [ ] VAE tiling enabled
- [ ] Started with nohup for persistence

### ✅ Environment Configuration
- [ ] HF_TOKEN environment variable set
- [ ] PUBLIC_IPADDR environment variable exists
- [ ] VAST_TCP_PORT_6006 environment variable exists
- [ ] Can determine public URL

### ✅ Network Configuration
- [ ] Local access works (curl localhost:6006/health)
- [ ] External access works (curl PUBLIC_IP:EXTERNAL_PORT/health)
- [ ] Port 6006 listening on 0.0.0.0
- [ ] No firewall blocking access

### ✅ Model Configuration
- [ ] HuggingFace account created
- [ ] FLUX.1-schnell license accepted
- [ ] HuggingFace token has "Read" permissions
- [ ] Models downloaded (~17GB)
- [ ] GPU detected and CUDA available

### ✅ Verification
- [ ] Health endpoint returns valid JSON
- [ ] Can generate test image
- [ ] Can check job status
- [ ] Can access generated image via public URL
- [ ] Server persists after SSH disconnect

---

## Step-by-Step Configuration Process

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/HarleyVader/flux1-vast-ai.git
cd flux1-vast-ai

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Set HuggingFace token
export HF_TOKEN='your_hf_token_here'

# Verify environment
echo "Public IP: $PUBLIC_IPADDR"
echo "External Port: $VAST_TCP_PORT_6006"
echo "Public URL: http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"
```

### 3. Server Startup

```bash
# Start server (will download models on first run)
nohup python3 server.py > server.log 2>&1 &

# Monitor startup
tail -f server.log

# Wait for "Model loaded successfully!"
```

### 4. Verification

```bash
# Test local access
curl http://localhost:6006/health

# Test external access
curl http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006/health
```

### 5. Test Image Generation

```bash
# Generate test image
curl -X POST http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "a test image", "steps": 4}'

# Note the job_id from response
# Wait ~45 seconds
# Access at: http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006/image/<job_id>
```

---

## Debugging Commands

### Check Server Status

```bash
# Is server running?
ps aux | grep "python3 server.py"

# What ports are listening?
netstat -tulpn | grep LISTEN

# Is port 6006 specifically listening?
netstat -tulpn | grep 6006
```

### Check Network Configuration

```bash
# Get all Vast.ai environment variables
env | grep VAST

# Get public access info
echo "http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"

# Test from inside container
curl -v http://localhost:6006/health

# Test public access from inside
curl -v http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006/health
```

### Check GPU Status

```bash
# GPU information
nvidia-smi

# Is CUDA available?
python3 -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"

# GPU memory usage
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### Monitor Server Logs

```bash
# Real-time monitoring
tail -f server.log

# Last 50 lines
tail -50 server.log

# Search for errors
grep -i error server.log

# Search for specific job
grep "job_id" server.log
```

---

## Advanced Configuration

### Custom Port (If 6006 Unavailable)

```bash
# 1. Check available ports
env | grep VAST_TCP_PORT

# 2. Choose an unused one (example: 1111)
# 3. Update server.py:
app.run(host='0.0.0.0', port=1111, debug=False)

# 4. Your public URL becomes:
echo "http://$PUBLIC_IPADDR:$VAST_TCP_PORT_1111"
```

### Production Deployment

**Use production WSGI server:**

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn (better than Flask dev server)
gunicorn -w 1 -b 0.0.0.0:6006 --timeout 300 server:app
```

**Note:** Use 1 worker because of GPU memory constraints.

---

## Configuration Summary

| Setting | Value | Reason |
|---------|-------|--------|
| **Internal Port** | 6006 | Vast.ai mapped port |
| **External Port** | 49483 | Auto-assigned by Vast.ai |
| **Host** | 0.0.0.0 | Accept external connections |
| **Memory Mode** | Sequential CPU offload | 8GB VRAM support |
| **VAE Optimization** | Slicing + Tiling | Reduce memory peaks |
| **Precision** | bfloat16 | Balance speed/memory |
| **Model** | FLUX.1-schnell | Fast inference |
| **Steps** | 4 | Optimal for schnell |
| **Process Management** | nohup | Persist after disconnect |

---

## Quick Reference

```bash
# Start server
nohup python3 server.py > server.log 2>&1 &

# Get public URL
echo "http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"

# Check health
curl http://localhost:6006/health

# View logs
tail -f server.log

# Check if running
ps aux | grep "python3 server.py"

# Stop server (get PID from ps command above)
kill <PID>

# Restart
kill <PID> && sleep 2 && nohup python3 server.py > server.log 2>&1 &
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-02  
**Tested Configuration:**
- Platform: Vast.ai
- GPU: NVIDIA GeForce RTX 3070 (8GB)
- CUDA: 12.1.1
- Driver: 535.230.02
- Public IP: 94.239.253.223
- External Port: 49483
