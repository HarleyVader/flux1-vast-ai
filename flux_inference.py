#!/usr/bin/env python3
"""
Flux.1 Inference Script
Supports Flux.1-schnell (fast, 4-step) optimized for 8GB VRAM
"""

import torch
from diffusers import FluxPipeline
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description='Generate images with Flux.1')
    parser.add_argument('--prompt', type=str, required=True, help='Text prompt for image generation')
    parser.add_argument('--model', type=str, default='black-forest-labs/FLUX.1-schnell', 
                       choices=['black-forest-labs/FLUX.1-schnell', 'black-forest-labs/FLUX.1-dev'],
                       help='Model to use (schnell is faster, dev is higher quality)')
    parser.add_argument('--steps', type=int, default=4, help='Number of inference steps (schnell: 1-4, dev: 20-50)')
    parser.add_argument('--guidance', type=float, default=0.0, help='Guidance scale (schnell uses 0.0)')
    parser.add_argument('--width', type=int, default=1024, help='Image width')
    parser.add_argument('--height', type=int, default=1024, help='Image height')
    parser.add_argument('--output', type=str, default='output.png', help='Output filename')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    print(f"Loading Flux.1 model: {args.model}")
    print(f"Using device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    
    # Load pipeline with memory optimizations for 8GB VRAM
    pipe = FluxPipeline.from_pretrained(
        args.model,
        torch_dtype=torch.bfloat16
    )
    
    # Enable aggressive memory optimizations
    pipe.enable_sequential_cpu_offload()  # Sequential offloading for lower VRAM
    pipe.vae.enable_slicing()
    pipe.vae.enable_tiling()
    
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Set seed if provided
    generator = None
    if args.seed is not None:
        generator = torch.Generator("cuda" if torch.cuda.is_available() else "cpu").manual_seed(args.seed)
        print(f"Using seed: {args.seed}")
    
    print(f"\nPrompt: {args.prompt}")
    print(f"Steps: {args.steps}, Guidance: {args.guidance}")
    print(f"Resolution: {args.width}x{args.height}")
    print("\nGenerating image...")
    
    # Generate image
    image = pipe(
        prompt=args.prompt,
        guidance_scale=args.guidance,
        num_inference_steps=args.steps,
        width=args.width,
        height=args.height,
        generator=generator,
    ).images[0]
    
    # Save image
    output_path = Path(args.output)
    image.save(output_path)
    print(f"\n✓ Image saved to: {output_path.absolute()}")

if __name__ == "__main__":
    main()
