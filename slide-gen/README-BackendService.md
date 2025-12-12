# Image Generation API Documentation

This document describes the image generation backend service requirements and integration for the Intelligent Slide Generation System.

## 📋 Overview

The slide generation system requires a REST API endpoint for generating images from text prompts. The API should be compatible with common image generation services like Stable Diffusion, DALL-E, or custom implementations.

## 🔌 API Specification

### Endpoint Configuration

Configure in `.env` file:

```env
IMAGE_API_KEY=your-api-key
IMAGE_API_URL=https://api.example.com/generate
IMAGE_MODEL=stable-diffusion-xl
```

### Authentication

The system supports **Bearer Token** authentication:

```http
Authorization: Bearer YOUR_API_KEY
```

## 📡 Request Format

### HTTP Method
`POST`

### Headers

```http
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
```

### Request Body Schema

```json
{
  "prompt": "A detailed description of the image to generate",
  "model": "stable-diffusion-xl",
  "width": 800,
  "height": 600,
  "n": 1
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text description of desired image |
| `model` | string | No | Model identifier (from config) |
| `width` | integer | Yes | Image width in pixels |
| `height` | integer | Yes | Image height in pixels |
| `n` | integer | No | Number of images to generate (default: 1) |

### Example Request

```bash
curl -X POST https://api.example.com/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "prompt": "A futuristic AI brain network visualization, high quality, professional, detailed",
    "width": 800,
    "height": 600,
    "n": 1
  }'
```

## 📥 Response Format

### Success Response

The API should return one of the following formats:

#### Format 1: URL Response

```json
{
  "data": [
    {
      "url": "https://api.example.com/images/generated-image-id.png"
    }
  ]
}
```

#### Format 2: Base64 Response

```json
{
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
    }
  ]
}
```

#### Format 3: Direct URL

```json
{
  "url": "https://api.example.com/images/generated-image-id.png"
}
```

#### Format 4: Alternative URL Field

```json
{
  "image_url": "https://api.example.com/images/generated-image-id.png"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | Success | Image generated successfully |
| 400 | Bad Request | Invalid parameters or prompt |
| 401 | Unauthorized | Invalid or missing API key |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side generation error |

### Error Response

```json
{
  "error": {
    "code": "invalid_prompt",
    "message": "The prompt contains prohibited content",
    "type": "invalid_request_error"
  }
}
```

## 🔄 Retry Logic

The system implements automatic retry logic:

- **Maximum Retries**: 3 (configurable via `MAX_RETRIES` in `.env`)
- **Backoff Strategy**: Exponential (2^attempt seconds)
- **Retry on**: Network errors, 500 errors, timeouts
- **No Retry on**: 400, 401, 403 errors

## 🖼️ Image Handling

### Image Formats
- **Supported**: PNG, JPEG, WebP
- **Preferred**: PNG (lossless)

### Image Dimensions

Common sizes used by the system:

| Template | Typical Sizes (W×H) |
|----------|-------------------|
| Title & Content | 400×300, 500×350, 600×450 |
| Two Column | 450×400, 500×450 |
| Image Focus | 800×600, 1000×750 |

### Image Processing

The system automatically:
1. Resizes images to exact requested dimensions
2. Converts to PNG format if needed
3. Saves to local filesystem (`output/images/`)
4. Falls back to placeholder on failure

## 🔐 API Key Security

### Best Practices

1. **Never hardcode keys** - Always use `.env` file
2. **Rotate regularly** - Change keys periodically
3. **Monitor usage** - Track API calls and costs
4. **Use separate keys** - Different keys for dev/prod
5. **Keep `.env` private** - Never commit to version control

### `.gitignore` Protection

The `.env` file is automatically ignored by Git. Verify:

```bash
# Check if .env is ignored
git check-ignore .env
# Should output: .env
```

## 🌐 Compatible Services

### OpenAI DALL-E

```env
IMAGE_API_URL=https://api.openai.com/v1/images/generations
IMAGE_API_KEY=sk-...
IMAGE_MODEL=dall-e-3
```

**Request format**:
```json
{
  "prompt": "Your prompt",
  "n": 1,
  "size": "1024x1024",
  "model": "dall-e-3"
}
```

**Note**: DALL-E has fixed sizes (1024×1024, 1024×1792, 1792×1024). System will resize after download.

### Stability AI

```env
IMAGE_API_URL=https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image
IMAGE_API_KEY=sk-...
IMAGE_MODEL=stable-diffusion-xl-1024-v1-0
```

**Request format**:
```json
{
  "text_prompts": [
    {
      "text": "Your prompt",
      "weight": 1
    }
  ],
  "cfg_scale": 7,
  "height": 1024,
  "width": 1024,
  "samples": 1
}
```

### Custom Backend

For custom implementations, ensure your API:

1. Accepts JSON POST requests
2. Supports Bearer token authentication
3. Returns image URL or base64 data
4. Handles arbitrary dimensions (or system will resize)
5. Provides error messages in JSON format

## 📊 Rate Limits and Quotas

### Recommended Limits

- **Requests per minute**: 20-60 (varies by provider)
- **Concurrent requests**: 3-5
- **Daily quota**: Check with your provider

### Handling Rate Limits

The system includes:
- Exponential backoff on 429 errors
- Sequential processing (not parallel) for images
- Configurable timeout (default: 60 seconds)

### Cost Estimation

For a 10-slide presentation with 2 images per slide:
- **Total API calls**: ~20 image generations
- **Estimated time**: 3-10 minutes (depending on API speed)
- **Estimated cost**: Varies by provider ($0.10-$2.00)

## 🧪 Testing the API

### Test Script

Create `test_image_api.py`:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("IMAGE_API_URL")
key = os.getenv("IMAGE_API_KEY")

response = requests.post(
    url,
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    },
    json={
        "prompt": "A test image of a blue sky",
        "width": 512,
        "height": 512,
        "n": 1
    }
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
```

Run:
```bash
python test_image_api.py
```

### Expected Output

```
Status: 200
Response: {'data': [{'url': 'https://...'}]}
```

## ⚠️ Common Issues

### Issue: 401 Unauthorized

**Cause**: Invalid API key

**Solution**: 
1. Verify `IMAGE_API_KEY` in `.env`
2. Check key is active and has permissions
3. Ensure no extra spaces in `.env` file

### Issue: 429 Too Many Requests

**Cause**: Rate limit exceeded

**Solution**:
1. Reduce `num_slides` parameter
2. Increase `DEFAULT_TIMEOUT` in `.env`
3. Wait before retrying
4. Upgrade API plan if needed

### Issue: Timeout Errors

**Cause**: Image generation taking too long

**Solution**:
1. Increase `DEFAULT_TIMEOUT` in `.env` (try 120)
2. Use faster model if available
3. Reduce image dimensions

### Issue: Invalid Image Dimensions

**Cause**: API doesn't support requested size

**Solution**:
- System automatically resizes after generation
- No action needed (handled internally)
- Check API logs for warnings

## 📚 Alternative APIs

### Replicate

```env
IMAGE_API_URL=https://api.replicate.com/v1/predictions
IMAGE_API_KEY=r8_...
```

### Hugging Face

```env
IMAGE_API_URL=https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0
IMAGE_API_KEY=hf_...
```

### Local Installation

For local Stable Diffusion:

```env
IMAGE_API_URL=http://localhost:7860/sdapi/v1/txt2img
IMAGE_API_KEY=optional-local-key
```

**Note**: Requires running Stable Diffusion WebUI locally.

## 🔧 Advanced Configuration

### Prompt Enhancement

The system automatically enhances prompts with:
- Style-specific keywords
- Quality indicators
- Technical specifications

Example transformation:
```
Input: "A neural network diagram"
Output: "A neural network diagram, corporate, clean, modern, 
         professional photography, high quality, detailed"
```

### Image Caching

To implement caching:

1. Store generated images with prompt hash as filename
2. Check cache before API call
3. Reuse cached images for identical prompts

**Note**: Not implemented by default to ensure fresh generation.

## 📈 Performance Tips

1. **Use appropriate dimensions**: Match template requirements
2. **Optimize prompts**: Clear, specific descriptions
3. **Monitor API usage**: Track costs and rate limits
4. **Handle failures gracefully**: System uses placeholders
5. **Consider local generation**: For high volume

## 🔗 Related Documentation

- [Main README](README.md) - Full system documentation
- [OpenAI Images API](https://platform.openai.com/docs/api-reference/images)
- [Stability AI Documentation](https://platform.stability.ai/docs/api-reference)
- [Replicate Documentation](https://replicate.com/docs)

---

**For questions about specific API providers, consult their official documentation.**

