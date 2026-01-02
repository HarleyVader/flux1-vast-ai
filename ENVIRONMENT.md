# Environment Configuration Reference

This file documents the Vast.ai environment configuration for this deployment.

## Instance Details

**Container Label:** C.29442464  
**GPU:** NVIDIA GeForce RTX 3070 (8GB VRAM)  
**Driver Version:** 535.230.02  
**CUDA Version:** 12.1.1  
**Compute Capability:** 8.6  

## Public Access

**Public IP Address:** 94.239.253.223  

## Port Mappings

Vast.ai internal ports are mapped to external ports as follows:

| Internal Port | External Port | Service |
|---------------|---------------|---------|
| 22 | 49577 | SSH |
| 1111 | 49105 | Instance Portal |
| 6006 | 49483 | **Flux.1 API Server** |
| 8080 | 49600 | Jupyter |
| 8384 | 49223 | Syncthing |
| 72299 | 49052 | Custom |

## Server Configuration

**Server Port:** 6006 (internal)  
**Public URL:** http://94.239.253.223:49483  

## Environment Variables

Key environment variables set by Vast.ai:

```bash
PUBLIC_IPADDR=94.239.253.223
VAST_CONTAINERLABEL=C.29442464
VAST_DEVICE_IDXS=0
VAST_TCP_PORT_6006=49483
CUDA_VERSION=12.1.1
```

## How to Find Your Configuration

When you deploy on Vast.ai, run these commands to find your settings:

```bash
# Get public IP
echo $PUBLIC_IPADDR

# Get port mapping for port 6006
echo $VAST_TCP_PORT_6006

# Full public URL
echo "http://$PUBLIC_IPADDR:$VAST_TCP_PORT_6006"

# View all Vast.ai variables
env | grep VAST

# GPU information
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
```

## Network Configuration

The server binds to `0.0.0.0:6006` internally, which allows Vast.ai to forward traffic from the external port (49483) to the internal port (6006).

## Firewall

Vast.ai handles firewall configuration automatically. No additional firewall rules needed.

## Storage

Models and generated images are stored in:
- Models: `~/.cache/huggingface/` (~17GB)
- Images: `/workspace/flux1-vast-ai/outputs/`

## Memory Management

Optimizations for 8GB VRAM:
- Sequential CPU offloading
- VAE slicing  
- VAE tiling
- bfloat16 precision

These keep VRAM usage under 8GB during inference.
