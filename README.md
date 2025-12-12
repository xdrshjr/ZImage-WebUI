<div align="center">

<img src="images/img-logo.png" alt="Z-Image Logo" width="80" height="80" style="border-radius: 50%; object-fit: cover;" />

# Z-Image Image Generation System

**An AI image generation system based on the Z-Image-Turbo model, featuring a Flask backend service and a Next.js frontend application, providing a complete image generation solution.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### ✨ Professional AI Image Generation at Your Fingertips ✨

| ⚡ Lightning Fast | 🔧 Custom Parameters |

</div>

---

## 📋 Project Overview

Z-Image is a complete AI image generation system consisting of two parts:

- **Backend Service**: Flask-based Z-Image-Turbo model API service providing image generation endpoints
- **Frontend Application**: Modern web application built with Next.js 14, providing an elegant user interface

The system adopts a frontend-backend separation architecture, supporting task queue management, real-time status tracking, batch generation, and other features suitable for production environment deployment.

<div align="center">

![img.png](images/img.png)[System Architecture]

</div>

---

## ✨ Features

### Core Image Generation

- ✅ **AI Image Generation**: Powered by Z-Image-Turbo model for high-quality text-to-image generation
- ✅ **Flexible Parameters**: Customizable image dimensions (width/height), inference steps (1-50), and random seed control
- ✅ **Batch Generation**: Generate multiple images (1-4) in a single request
- ✅ **Fast Inference**: Optimized for speed with GPU acceleration and memory persistence
- ✅ **High Quality Output**: Produces professional-quality images suitable for various use cases


### Intelligent Slide Generation

The system includes an **AI-powered presentation generator** that creates visually appealing, content-rich slides from textual input using Python and LangGraph.

**Key Features:**

- ✅ **AI-Driven Content Generation**: Uses LLM to generate structured outlines, layouts, and content
- ✅ **Intelligent Image Generation**: Automatically creates relevant images with refined prompts
- ✅ **Multiple Template Types**: Three professionally designed templates (Title & Content, Two Column, Image Focus)
- ✅ **Multiple Output Formats**: Generates HTML, PNG images, and consolidated PDF
- ✅ **Style Customization**: Support for different visual styles (professional, creative, minimal, academic)
- ✅ **Flexible Configuration**: Customizable aspect ratios, content richness, and slide count
- ✅ **Robust Error Handling**: Graceful degradation with placeholder images and comprehensive logging

**Architecture:**

The slide generation system uses **LangGraph** to orchestrate a multi-phase workflow:

1. **Phase 1: Outline Planning** - Generate structured outline for all slides
2. **Phase 2: Page-by-Page Generation** - For each slide:
   - Generate layout and content
   - Refine image prompts
   - Generate images via API
   - Assemble HTML slide
3. **Phase 3: Final Export** - Export to PNG and compile PDF

**Output Files:**

After successful generation, you'll find:
- **`output/html/`** - Individual HTML files for each slide
- **`output/images/`** - AI-generated images used in slides
- **`output/slide_images/`** - PNG exports of complete slides
- **`output/final_presentation.pdf`** - Multi-page PDF presentation

For detailed documentation, see the [`slide-gen/README.md`](slide-gen/README.md) file.

## Tech Stack

### Frontend Tech Stack

- **Next.js 14+** (App Router)
- **React 18+**
- **TypeScript**
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Component library based on Radix UI
- **Lucide React** - Icon library
- **axios** - HTTP client
- **react-hot-toast** - Toast notifications

### Backend Tech Stack

- **Flask** - Python web framework
- **PyTorch** - Deep learning framework
- **CUDA** - GPU acceleration
- **Diffusers** - Hugging Face diffusion models library
- **Gunicorn** - WSGI HTTP server (production)

## Environment Requirements

### Frontend Requirements

- Node.js 18+
- npm / yarn / pnpm

### Backend Requirements

- Python 3.8+
- CUDA 11.8+ (GPU environment)
- At least 16GB GPU VRAM
- 8GB+ system RAM

## Quick Start

### 1. Clone the Project

```bash
git clone <repository-url>
cd Z-Image-BackendService
```

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Slide Generation Service (Optional)

If you want to use the intelligent slide generation feature, run the setup script to install all required dependencies:

```bash
# Make the script executable (Linux/macOS)
chmod +x setup_slide_generation.sh

# Run the setup script
./setup_slide_generation.sh
```

**What the script does:**

- ✅ Checks Python version compatibility (requires Python 3.9+)
- ✅ Installs all slide-gen dependencies from `slide-gen/requirements.txt`
- ✅ Installs Playwright Chromium browser (required for PNG export, ~150MB download)
- ✅ Verifies `.env` configuration file and checks for required API keys

**Required Configuration:**

After running the setup script, make sure to configure the following in your `.env` file:

```env
# Slide Generation - LLM Configuration
SLIDE_LLM_API_KEY=your-openai-api-key
SLIDE_LLM_API_URL=https://api.openai.com/v1/chat/completions
SLIDE_LLM_MODEL=gpt-4

# Slide Generation - Image API Configuration  
SLIDE_IMAGE_API_KEY=your-image-api-key
SLIDE_IMAGE_API_URL=http://localhost:5000
SLIDE_IMAGE_MODEL=stable-diffusion-xl
```

**Note:** The slide generation service requires:
- Python 3.9 or higher
- OpenAI-compatible LLM API access
- Image generation API access (can use the Z-Image backend service)

For detailed slide generation documentation, refer to [`slide-gen/README.md`](slide-gen/README.md).

### 4. Configure Backend Service (Optional)

Create a `.env` file or set environment variables directly:

```bash
# GPU Configuration
GPU_DEVICE_ID=0
CUDA_AVAILABLE=true

# Model Configuration
MODEL_NAME=Tongyi-MAI/Z-Image-Turbo
MODEL_TORCH_DTYPE=bfloat16

# Service Configuration
HOST=0.0.0.0
PORT=5000
DEBUG=false

# Queue Configuration
MAX_QUEUE_SIZE=100
TASK_TIMEOUT=300

# Output Directory
OUTPUT_DIR=./outputs
```

### 5. Start Backend Service

#### Development Mode

```bash
python app.py
```

#### Production Mode (Using Gunicorn)

```bash
gunicorn -w 1 -b 0.0.0.0:5000 --timeout 600 app:app
```

**Note**: Since the model requires exclusive GPU access, the worker count should be set to 1.

After starting, the backend service runs at `http://localhost:5000` by default.

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
# or
yarn install
# or
pnpm install
```

### 7. Configure Frontend Backend Service Address

There are two ways to configure the backend service address:

**Method 1: Using Environment Variables (Recommended)**

Create a `.env.local` file in the `frontend` directory:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:5000
```

Or copy the `.env.example` file:

```bash
cp .env.example .env.local
```

Then modify the address in `.env.local`.

**Method 2: Configure Within the Application**

- After starting the frontend application, click the settings icon in the top-right corner
- Enter the backend service address, e.g., `http://localhost:5000`
- Click "Test Connection" to verify the configuration
- Click "Save" to save the configuration

**Configuration Priority**: Environment variables > localStorage configuration > Default value (`http://localhost:5000`)

### 8. Start Frontend Service

```bash
cd frontend
npm run dev
# or
yarn dev
# or
pnpm dev
```

After starting, visit `http://localhost:3000`.

## One-Click Startup (Recommended)

The project root directory provides a `start.sh` startup script for one-click building of the frontend and starting both backend and frontend services.

### Usage

1. **Grant Execute Permission** (first-time use):

```bash
chmod +x start.sh
```

2. **Execute Startup Script**:

```bash
./start.sh
```

### Script Features

- ✅ Automatically checks environment dependencies (Node.js, npm, Python)
- ✅ Automatically builds frontend application (`npm run build`)
- ✅ Starts Flask backend service (port 5000)
- ✅ Starts Next.js frontend service (port 3000)
- ✅ Detailed logging and error handling

### Service Addresses

- Backend Service: http://localhost:5000
- Frontend Service: http://localhost:3000

### Stopping Services

The project root directory provides a `stop.sh` script for one-click stopping of backend and frontend services:

```bash
# Grant execute permission (first-time use)
chmod +x stop.sh

# Execute stop script
./stop.sh
```

Stop script features:
- ✅ Automatically finds and stops backend service (port 5000)
- ✅ Automatically finds and stops frontend service (port 3000)
- ✅ Supports multiple process finding methods (lsof, netstat, ps)
- ✅ Automatically attempts force stop if normal stop fails
- ✅ Detailed logging


## API Overview

The backend service provides the following main API endpoints:

### 1. Health Check

```
GET /health
```

Check service health status and model loading status.

### 2. Submit Generation Task

```
POST /api/generate
```

Submit an image generation task and return a task ID.

**Request Parameters**:
- `prompt` (required): Text prompt
- `height` (optional): Image height, default 1024
- `width` (optional): Image width, default 1024
- `num_inference_steps` (optional): Inference steps, default 9
- `seed` (optional): Random seed

### 3. Query Task Status

```
GET /api/task/<task_id>
```

Query the status and details of a specific task.

### 4. Get Generation Result

```
GET /api/result/<task_id>
```

Get the generated image file (when task is completed).

### 5. Query System Status

```
GET /api/status
```

Query overall system status, including queue information, GPU usage, etc.

For detailed API documentation, refer to `README-BackendService.md`.

## Usage Instructions

### Generating Images

1. Enter your desired image description in the prompt input box
2. Set generation parameters:
   - **Number of Images**: Select 1-4 images to generate
   - **Image Size**: Choose preset size or customize width and height
   - **Inference Steps**: 1-50, higher values produce better quality but slower speed (default 9)
   - **Random Seed**: Optional, same seed and prompt will generate identical images
3. Click the "Start Generation" button
4. After task submission, view progress in the task list on the right

### Prompt Enhancement

1. Click the "Enhance" button to the right of the prompt input box
2. Choose one of the following methods:
   - **Use Template**: Select preset prompt templates from the template library
   - **Enhance Prompt**: Automatically add quality and style terms to the current prompt

### Preview and Download Images

1. After task completion, click the "Preview" button in the task list
2. View full-size images in the preview modal
3. Click the "Download" button to save images locally
4. Keyboard shortcut support: Press `ESC` to close preview

## FAQ

### What if Backend Connection Fails?

- Check if the backend service has started
- Verify the backend service address configuration is correct
- Check network connectivity
- Check firewall settings
- Use the "Test Connection" feature to verify configuration

### Common Reasons for Generation Failure

- **Queue Full**: Wait for tasks in the queue to complete and try again
- **Model Not Loaded**: Check backend service logs to confirm successful model loading
- **Insufficient GPU Memory**: Reduce image size or inference steps
- **Parameter Error**: Verify parameters are within allowed ranges

### Task Always Shows "Waiting"?

- Check if the backend service is running normally
- View task queue position; if position is high, longer wait time may be needed
- Check if other tasks are being processed

### Model Loading Failure

- Check if CUDA is available: `python -c "import torch; print(torch.cuda.is_available())"`
- Verify GPU VRAM is sufficient (at least 16GB)
- Check if model path is correct

### Insufficient GPU Memory

- Enable CPU Offloading: `ENABLE_CPU_OFFLOAD=true`
- Reduce concurrent task count
- Lower image resolution


## Performance Optimization Recommendations

1. **Model Compilation**: Enable `ENABLE_MODEL_COMPILE=true` in configuration to accelerate inference, though first run will be slower
2. **Flash Attention**: Flash Attention-2 is enabled by default for improved performance
3. **Queue Management**: Adjust `MAX_QUEUE_SIZE` based on GPU VRAM to avoid memory overflow
4. **Batch Processing**: While current version doesn't support batching, throughput can be improved by concurrently submitting multiple tasks

## Browser Support

- Chrome/Edge (latest version)
- Firefox (latest version)
- Safari (latest version)

**Note**: This application only supports desktop browsers. Mobile browsers will display a blocking page.

## License

This project is based on the Z-Image-Turbo model. Please comply with the corresponding license requirements.

## Contact

Email: xdrshjr@gmail.com

For questions or suggestions, please submit an Issue or Pull Request.

