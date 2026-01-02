#!/usr/bin/env python3
"""
Simple HTTP server for Flux.1 image generation
Generates images and returns UUID-based URLs
"""

from flask import Flask, request, jsonify, send_file
import torch
from diffusers import FluxPipeline
import uuid
import os
from pathlib import Path
import threading
import queue
import time

app = Flask(__name__)

# Configuration
OUTPUT_DIR = Path("/workspace/outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# Global pipeline (loaded once)
pipe = None
pipe_lock = threading.Lock()

# Job queue for async generation
job_queue = queue.Queue()
job_status = {}  # {job_id: {"status": "pending|processing|complete|error", "image_path": "...", "error": "..."}}

def load_model():
    """Load Flux.1 model once at startup"""
    global pipe
    print("Loading Flux.1 model...")
    pipe = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-schnell",
        torch_dtype=torch.bfloat16
    )
    pipe.enable_sequential_cpu_offload()
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()
    print("Model loaded successfully!")

def worker():
    """Background worker to process generation jobs"""
    while True:
        job = job_queue.get()
        if job is None:
            break
            
        job_id = job["id"]
        prompt = job["prompt"]
        steps = job.get("steps", 4)
        width = job.get("width", 1024)
        height = job.get("height", 1024)
        seed = job.get("seed")
        
        job_status[job_id]["status"] = "processing"
        
        try:
            with pipe_lock:
                generator = None
                if seed is not None:
                    generator = torch.Generator("cuda").manual_seed(seed)
                
                image = pipe(
                    prompt=prompt,
                    guidance_scale=0.0,
                    num_inference_steps=steps,
                    width=width,
                    height=height,
                    generator=generator,
                ).images[0]
            
            # Save image
            image_path = OUTPUT_DIR / f"{job_id}.png"
            image.save(image_path)
            
            job_status[job_id]["status"] = "complete"
            job_status[job_id]["image_path"] = str(image_path)
            
        except Exception as e:
            job_status[job_id]["status"] = "error"
            job_status[job_id]["error"] = str(e)
        
        job_queue.task_done()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "model_loaded": pipe is not None,
        "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None"
    })

@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate image from prompt
    
    POST /generate
    {
        "prompt": "a cat wearing sunglasses",
        "steps": 4,  // optional, default 4
        "width": 1024,  // optional, default 1024
        "height": 1024,  // optional, default 1024
        "seed": 42  // optional
    }
    
    Returns:
    {
        "job_id": "uuid",
        "status_url": "/status/uuid",
        "image_url": "/image/uuid"
    }
    """
    data = request.get_json()
    
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Create job
    job = {
        "id": job_id,
        "prompt": data["prompt"],
        "steps": data.get("steps", 4),
        "width": data.get("width", 1024),
        "height": data.get("height", 1024),
        "seed": data.get("seed")
    }
    
    # Initialize job status
    job_status[job_id] = {
        "status": "pending",
        "prompt": data["prompt"],
        "created_at": time.time()
    }
    
    # Queue job
    job_queue.put(job)
    
    return jsonify({
        "job_id": job_id,
        "status_url": f"/status/{job_id}",
        "image_url": f"/image/{job_id}"
    }), 202

@app.route('/status/<job_id>', methods=['GET'])
def status(job_id):
    """
    Get job status
    
    GET /status/<job_id>
    
    Returns:
    {
        "job_id": "uuid",
        "status": "pending|processing|complete|error",
        "prompt": "...",
        "image_url": "/image/uuid",  // only if complete
        "error": "..."  // only if error
    }
    """
    if job_id not in job_status:
        return jsonify({"error": "Job not found"}), 404
    
    result = {
        "job_id": job_id,
        "status": job_status[job_id]["status"],
        "prompt": job_status[job_id].get("prompt", "")
    }
    
    if job_status[job_id]["status"] == "complete":
        result["image_url"] = f"/image/{job_id}"
    elif job_status[job_id]["status"] == "error":
        result["error"] = job_status[job_id].get("error", "Unknown error")
    
    return jsonify(result)

@app.route('/image/<job_id>', methods=['GET'])
def get_image(job_id):
    """
    Get generated image
    
    GET /image/<job_id>
    
    Returns: PNG image file
    """
    if job_id not in job_status:
        return jsonify({"error": "Job not found"}), 404
    
    if job_status[job_id]["status"] != "complete":
        return jsonify({
            "error": "Image not ready",
            "status": job_status[job_id]["status"]
        }), 404
    
    image_path = job_status[job_id].get("image_path")
    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": "Image file not found"}), 404
    
    return send_file(image_path, mimetype='image/png')

@app.route('/', methods=['GET'])
def index():
    """API documentation"""
    return jsonify({
        "name": "Flux.1 Image Generation API",
        "version": "1.0",
        "endpoints": {
            "GET /health": "Health check",
            "POST /generate": "Generate image from prompt (returns job_id)",
            "GET /status/<job_id>": "Check generation status",
            "GET /image/<job_id>": "Download generated image"
        },
        "example": {
            "request": {
                "method": "POST",
                "url": "/generate",
                "body": {
                    "prompt": "a cat wearing sunglasses",
                    "steps": 4,
                    "width": 1024,
                    "height": 1024,
                    "seed": 42
                }
            },
            "response": {
                "job_id": "550e8400-e29b-41d4-a716-446655440000",
                "status_url": "/status/550e8400-e29b-41d4-a716-446655440000",
                "image_url": "/image/550e8400-e29b-41d4-a716-446655440000"
            }
        }
    })

if __name__ == '__main__':
    # Load model at startup
    load_model()
    
    # Start background worker
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    
    # Run server
    print("\n" + "="*60)
    print("Flux.1 Image Generation Server")
    print("="*60)
    print("Server starting on http://0.0.0.0:5000")
    print("\nAPI Endpoints:")
    print("  POST /generate      - Generate image")
    print("  GET  /status/<id>   - Check status")
    print("  GET  /image/<id>    - Get image")
    print("  GET  /health        - Health check")
    print("="*60 + "\n")
    
    # Run server on port 6006 (mapped to public port via VAST_TCP_PORT_6006)
    app.run(host='0.0.0.0', port=6006, debug=False)
