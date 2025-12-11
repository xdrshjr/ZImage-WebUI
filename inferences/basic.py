import torch
from diffusers import ZImagePipeline

# 1. Load the pipeline
# Use bfloat16 for optimal performance on supported GPUs
pipe = ZImagePipeline.from_pretrained(
    "Tongyi-MAI/Z-Image-Turbo",
    torch_dtype=torch.bfloat16,
    low_cpu_mem_usage=False,
)
pipe.to("cuda")

# [Optional] Attention Backend
# Diffusers uses SDPA by default. Switch to Flash Attention for better efficiency if supported:
pipe.transformer.set_attention_backend("flash")    # Enable Flash-Attention-2
# pipe.transformer.set_attention_backend("_flash_3") # Enable Flash-Attention-3

# [Optional] Model Compilation
# Compiling the DiT model accelerates inference, but the first run will take longer to compile.
# pipe.transformer.compile()

# [Optional] CPU Offloading
# Enable CPU offloading for memory-constrained devices.
# pipe.enable_model_cpu_offload()

# prompt = "Young Chinese woman in red Hanfu, intricate embroidery. Impeccable makeup, red floral forehead pattern. Elaborate high bun, golden phoenix headdress, red flowers, beads. Holds round folding fan with lady, trees, bird. Neon lightning-bolt lamp (⚡️), bright yellow glow, above extended left palm. Soft-lit outdoor night background, silhouetted tiered pagoda (西安大雁塔), blurred colorful distant lights."

prompt = "Create a technical diagram illustrating a neural network latent thought mechanism. The image should show a horizontal timeline divided into three distinct zones from left to right:Zone 1 (Normal Mode - Before Latent): Light blue background, showing a sequence of token embeddings labeled as e(x₁), e(x₂), ..., e(xᵢ), with a prominent special token marker '<bot>' at position i.Zone 2 (Latent Mode): Highlighted in soft purple/lavender background, showing hidden states labeled as hᵢ, hᵢ₊₁, ..., h_{t-1}, h_{j-1}. This zone should appear visually distinct, like a processing chamber or tunnel. Include a subtle indication that these replace the normal embeddings.Zone 3 (Normal Mode - After Latent): Return to light blue background, showing a mix: the hidden states from the latent zone (hᵢ through h_{j-1}), followed by the special token '<eot>' at position j, then resuming normal token embeddings e(xⱼ), e(xⱼ₊₁), ..., e(x_t).Include:Clear vertical boundary lines at positions i and j marked with the special tokenArrows showing the flow direction (left to rightSmall annotations indicating 'input embedding layer' and 'hidden state layerA legend explaining the color zones: 'Normal Mode' vs 'Latent Thought Mode'Clean, professional style suitable for an academic paper or technical presentationMinimalist color scheme: blues, purples, whites, with black textClear labels using mathematical notation (subscripts, Greek letters if needed)Style: Technical schematic diagram, clean lines, educational infographic, similar to machine learning architecture diagrams found in research papers."

# 2. Generate Image
image = pipe(
    prompt=prompt,
    height=1024,
    width=1024,
    num_inference_steps=9,  # This actually results in 8 DiT forwards
    guidance_scale=0.0,  # Guidance should be 0 for the Turbo models
    generator=torch.Generator("cuda").manual_seed(42),
).images[0]

# save
image.save("../output/example.png")
