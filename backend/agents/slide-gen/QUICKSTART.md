# Quick Start Guide

Get the slide generation system running in 5 minutes.

## 1. Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 2. Installation Steps

### Step 1: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Playwright Browsers

```bash
playwright install chromium
```

## 3. Configuration

### Step 1: Copy Environment Template

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### Step 2: Edit `.env` File

Open `.env` in your text editor and add your API credentials:

```env
# Replace these with your actual credentials
LLM_API_KEY=sk-your-actual-api-key
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4

IMAGE_API_KEY=your-actual-image-api-key
IMAGE_API_URL=https://api.example.com/generate
IMAGE_MODEL=stable-diffusion-xl
```

**Important**: Replace placeholder values with real credentials!

## 4. Verify Setup

```bash
python setup.py
```

Expected output:
```
✓ Python 3.9+
✓ All dependencies installed
✓ .env file exists
✓ Environment variables configured
✓ ALL CHECKS PASSED
```

## 5. Run the System

```bash
python main.py
```

This will generate a 6-slide presentation about AI and save it to the `output/` directory.

## 6. View Results

After successful generation:

- **HTML slides**: `output/html/slide_1.html`, etc.
- **Images**: `output/images/`
- **Slide PNGs**: `output/slide_images/`
- **Final PDF**: `output/final_presentation.pdf`

## 7. Customize Parameters

Edit `main.py` to change generation parameters:

```python
params = {
    "base_text": "Your custom topic here",
    "num_slides": 8,                    # Change slide count
    "aspect_ratio": "16:9",             # 16:9, 4:3, or 16:10
    "style": "creative",                # professional, creative, minimal, academic
    "content_richness": "detailed"      # concise, moderate, detailed
}
```

## Troubleshooting

### Issue: "Module not found"
**Solution**: Activate virtual environment and install dependencies
```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install
pip install -r requirements.txt
```

### Issue: "API key error"
**Solution**: Check `.env` file has valid API keys (no placeholders)

### Issue: "Playwright not installed"
**Solution**: Install Playwright browsers
```bash
playwright install chromium
```

## Next Steps

- Read [README.md](README.md) for full documentation
- See [README-BackendService.md](README-BackendService.md) for image API details
- Customize templates in `src/templates/`
- Adjust prompts in `src/llm/prompts.py`

---

**Need help?** Check the main README or troubleshooting section.

