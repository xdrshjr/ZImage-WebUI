<div align="center">

<img src="images/img-logo.png" alt="Z-Image Logo" width="80" height="80" style="border-radius: 50%; object-fit: cover;" />

# Z-Image Image Generation System

**An AI image generation system based on the Z-Image-Turbo model, featuring a Flask backend service and a Next.js frontend application, providing a complete image generation solution.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

### ✨ Professional AI Image Generation at Your Fingertips ✨

| 🎨 Apple-Style Design | ⚡ Lightning Fast | 🔧 Custom Parameters | 📱 Desktop Optimized |

</div>

---

## 📋 Project Overview

Z-Image is a complete AI image generation system consisting of two parts:

- **Backend Service**: Flask-based Z-Image-Turbo model API service providing image generation endpoints
- **Frontend Application**: Modern web application built with Next.js 14, providing an elegant user interface

The system adopts a frontend-backend separation architecture, supporting task queue management, real-time status tracking, batch generation, and other features suitable for production environment deployment.

<div align="center">

![System Architecture](images/img.png)

</div>

---

## ✨ Features

### Frontend Features

- ✅ **Apple-Style Design**: Clean and elegant UI design following Apple's design language
- ✅ **Mobile Blocking**: Desktop-only access with friendly prompts for mobile devices
- ✅ **Backend Service Configuration**: Configurable backend service IP and port with connection testing
- ✅ **Text-to-Image Generation**: Support for batch generation of multiple images (1-4 images)
- ✅ **Custom Parameters**: Support for image size, inference steps, random seed, and other parameter settings
- ✅ **Prompt Enhancement**: Template library and prompt enhancement features
- ✅ **Task Status Tracking**: Real-time polling of task status, displaying queue position and progress
- ✅ **Image Preview & Download**: Support for image preview and download
- ✅ **Error Handling**: Comprehensive error prompts and exception handling
- ✅ **Responsive Design**: Adapted to different desktop screen sizes

### Backend Features

- ✅ **Model Memory Persistence**: Model loaded once at startup and kept in GPU memory globally
- ✅ **Task Queue Mechanism**: Thread-safe task queue supporting concurrent requests
- ✅ **Status Tracking**: Comprehensive task status tracking and query endpoints
- ✅ **Error Handling**: Complete error handling and logging
- ✅ **GPU Monitoring**: Support for GPU usage monitoring
- ✅ **Queue Management**: Task timeout and queue management mechanisms
- ✅ **Unified API**: Unified JSON API response format

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

### 3. Configure Backend Service (Optional)

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

### 4. Start Backend Service

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

### 5. Install Frontend Dependencies

```bash
cd frontend
npm install
# or
yarn install
# or
pnpm install
```

### 6. Configure Frontend Backend Service Address

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

### 7. Start Frontend Service

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

## Deployment Guide

### Backend Service Deployment

#### Deploying with Gunicorn

```bash
gunicorn -w 1 -b 0.0.0.0:5000 --timeout 600 app:app
```

#### Managing with systemd (Linux)

Create service file `/etc/systemd/system/z-image-backend.service`:

```ini
[Unit]
Description=Z-Image Backend Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/Z-Image-BackendService
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 1 -b 0.0.0.0:5000 --timeout 600 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl start z-image-backend
sudo systemctl enable z-image-backend
```

#### Using Nginx Reverse Proxy (Optional)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Frontend Service Deployment

#### Build Production Version

```bash
cd frontend
npm run build
```

#### Start Production Server

```bash
npm start
```

#### Managing with PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start application
cd frontend
pm2 start npm --name "z-image-frontend" -- start

# Check status
pm2 status

# View logs
pm2 logs z-image-frontend

# Stop application
pm2 stop z-image-frontend

# Restart application
pm2 restart z-image-frontend
```

#### Deploying Static Files with Nginx

```bash
# Build static files
cd frontend
npm run build

# Export static files
npm run export  # If static export is configured
```

Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/frontend/out;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API to backend service
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Deployment (Optional)

#### Backend Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--timeout", "600", "app:app"]
```

#### Frontend Dockerfile

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package*.json ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3000

CMD ["npm", "start"]
```

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

## Project Structure

```
Z-Image-BackendService/
├── app.py                    # Flask application main file
├── model_manager.py          # Model loading and management
├── task_queue.py             # Task queue management
├── config.py                 # Configuration file
├── requirements.txt          # Python dependencies list
├── outputs/                  # Generated images storage directory
├── README-BackendService.md  # Backend detailed documentation
├── start.sh                  # One-click startup script
├── stop.sh                   # One-click stop script
└── frontend/                 # Frontend application directory
    ├── app/                  # Next.js App Router
    ├── components/           # React components
    ├── hooks/                # Custom Hooks
    ├── lib/                  # Utility functions and configuration
    ├── types/                # TypeScript type definitions
    ├── public/               # Static assets
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.js
    ├── next.config.js
    └── README.md             # Frontend detailed documentation
```

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

For questions or suggestions, please submit an Issue or Pull Request.
```