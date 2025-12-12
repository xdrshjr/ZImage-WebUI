# Examples and JSON Schemas

This document provides examples of the JSON schemas used throughout the slide generation process.

## 1. Outline Generation (Phase 1)

### Input Parameters
```json
{
  "base_text": "Introduction to Artificial Intelligence and its applications",
  "num_slides": 6,
  "aspect_ratio": "16:9",
  "style": "professional",
  "content_richness": "moderate"
}
```

### Expected LLM Output (Outline)

```json
{
  "outline": [
    {
      "slide_number": 1,
      "title": "Introduction to AI",
      "key_points": [
        "What is Artificial Intelligence?",
        "Brief history and evolution",
        "Why AI matters today"
      ]
    },
    {
      "slide_number": 2,
      "title": "Core AI Concepts",
      "key_points": [
        "Machine Learning basics",
        "Neural networks overview",
        "Data-driven decision making"
      ]
    },
    {
      "slide_number": 3,
      "title": "AI Applications",
      "key_points": [
        "Healthcare and diagnostics",
        "Autonomous vehicles",
        "Natural language processing"
      ]
    },
    {
      "slide_number": 4,
      "title": "Machine Learning Types",
      "key_points": [
        "Supervised learning",
        "Unsupervised learning",
        "Reinforcement learning"
      ]
    },
    {
      "slide_number": 5,
      "title": "AI in Business",
      "key_points": [
        "Process automation",
        "Predictive analytics",
        "Customer personalization"
      ]
    },
    {
      "slide_number": 6,
      "title": "Future of AI",
      "key_points": [
        "Emerging trends",
        "Ethical considerations",
        "What's next?"
      ]
    }
  ]
}
```

## 2. Slide Layout Generation (Phase 2.1)

### Template 1: Title and Content

```json
{
  "slide_number": 2,
  "template_type": "title_and_content",
  "layout": {
    "title": "Core AI Concepts",
    "content_blocks": [
      {
        "type": "text",
        "content": "Machine Learning is a subset of AI that enables computers to learn from data without explicit programming.\n\n• Neural networks mimic brain structure\n• Algorithms improve with experience\n• Pattern recognition is key",
        "position": {
          "x": 0,
          "y": 100,
          "width": 1200,
          "height": 400
        },
        "char_limit": 400
      },
      {
        "type": "image_placeholder",
        "position": {
          "x": 1250,
          "y": 200,
          "width": 600,
          "height": 450
        },
        "image_prompt": "Neural network visualization with interconnected nodes"
      }
    ]
  }
}
```

### Template 2: Two Column

```json
{
  "slide_number": 4,
  "template_type": "two_column",
  "layout": {
    "title": "Machine Learning Types",
    "content_blocks": [
      {
        "type": "text",
        "content": "Supervised Learning:\n• Uses labeled data\n• Learns from examples\n• Makes predictions\n\nUnsupervised Learning:\n• Finds hidden patterns\n• No labeled data needed\n• Clustering and grouping",
        "position": {
          "x": 0,
          "y": 100,
          "width": 850,
          "height": 600
        },
        "char_limit": 300
      },
      {
        "type": "image_placeholder",
        "position": {
          "x": 960,
          "y": 200,
          "width": 450,
          "height": 400
        },
        "image_prompt": "Comparison diagram showing supervised vs unsupervised learning"
      }
    ]
  }
}
```

### Template 3: Image Focus

```json
{
  "slide_number": 1,
  "template_type": "image_focus",
  "layout": {
    "title": "Introduction to AI",
    "content_blocks": [
      {
        "type": "image_placeholder",
        "position": {
          "x": 560,
          "y": 250,
          "width": 800,
          "height": 600
        },
        "image_prompt": "Futuristic AI brain with glowing neural connections"
      },
      {
        "type": "text",
        "content": "Artificial Intelligence is transforming how we live and work",
        "position": {
          "x": 0,
          "y": 900,
          "width": 1920,
          "height": 100
        },
        "char_limit": 100
      }
    ]
  }
}
```

## 3. Image Prompt Refinement (Phase 2.2)

### Original Prompt
```
"Neural network visualization with interconnected nodes"
```

### Refined Prompt (LLM Output)
```
"A professional neural network visualization showing interconnected nodes 
with glowing connections, clean modern design, corporate blue and white 
color palette, isometric view, high-tech aesthetic, detailed node structure, 
flowing data streams, minimalist background, high quality digital illustration, 
sharp focus, professional lighting"
```

## 4. Image Generation API Request (Phase 2.3)

### Request to Image API

```json
{
  "prompt": "A professional neural network visualization showing interconnected nodes with glowing connections, clean modern design, corporate blue and white color palette, isometric view, high-tech aesthetic, detailed node structure, flowing data streams, minimalist background, high quality digital illustration, sharp focus, professional lighting",
  "model": "stable-diffusion-xl",
  "width": 600,
  "height": 450,
  "n": 1
}
```

### Expected API Response (Format 1)

```json
{
  "data": [
    {
      "url": "https://api.example.com/images/abc123.png"
    }
  ]
}
```

### Expected API Response (Format 2 - Base64)

```json
{
  "data": [
    {
      "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
    }
  ]
}
```

## 5. Complete Slide Data Structure

After all phases, each slide has this structure:

```json
{
  "slide_number": 2,
  "template_type": "title_and_content",
  "layout": {
    "title": "Core AI Concepts",
    "content_blocks": [
      {
        "type": "text",
        "content": "Machine Learning is a subset of AI...",
        "position": {"x": 0, "y": 100, "width": 1200, "height": 400},
        "char_limit": 400
      },
      {
        "type": "image_placeholder",
        "position": {"x": 1250, "y": 200, "width": 600, "height": 450},
        "image_prompt": "Neural network visualization...",
        "image_path": "output/images/slide_2_img_1.png"
      }
    ]
  },
  "html_path": "output/html/slide_2.html",
  "image_path": "output/slide_images/slide_2.png"
}
```

## 6. Final Result Object

After complete generation:

```json
{
  "success": true,
  "output_path": "g:\\projects\\slide-gen\\output",
  "pdf_path": "g:\\projects\\slide-gen\\output\\final_presentation.pdf",
  "slides_generated": 6,
  "errors": []
}
```

### With Errors (Graceful Degradation)

```json
{
  "success": false,
  "output_path": "g:\\projects\\slide-gen\\output",
  "pdf_path": "g:\\projects\\slide-gen\\output\\final_presentation.pdf",
  "slides_generated": 6,
  "errors": [
    "Image generation failed for slide 3, block 0: API timeout",
    "Image generation failed for slide 5, block 1: Rate limit exceeded"
  ]
}
```

## 7. Character Limits by Content Richness

### Concise
```json
{
  "title": 50,
  "body": 250,
  "caption": 80
}
```

### Moderate (Default)
```json
{
  "title": 60,
  "body": 400,
  "caption": 100
}
```

### Detailed
```json
{
  "title": 70,
  "body": 600,
  "caption": 150
}
```

## 8. Aspect Ratio Dimensions

### 16:9 (Default - HD)
```json
{
  "width": 1920,
  "height": 1080
}
```

### 4:3 (Traditional)
```json
{
  "width": 1600,
  "height": 1200
}
```

### 16:10 (Widescreen)
```json
{
  "width": 1920,
  "height": 1200
}
```

## 9. Style-Specific CSS Classes

### Professional Style
```css
.slide.professional {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #ffffff;
}
```

### Creative Style
```css
.slide.creative {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: #ffffff;
}
```

### Minimal Style
```css
.slide.minimal {
    background: #ffffff;
    color: #333333;
}
```

### Academic Style
```css
.slide.academic {
    background: #f8f9fa;
    color: #212529;
    border: 8px solid #003d82;
}
```

## 10. Error Response Examples

### LLM API Error
```json
{
  "error": {
    "message": "Invalid API key provided",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

### Image API Error
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please try again in 60 seconds.",
    "type": "rate_limit_error"
  }
}
```

## Usage in Code

### Accessing Outline
```python
outline = state['outline']
for slide_entry in outline:
    print(f"Slide {slide_entry['slide_number']}: {slide_entry['title']}")
```

### Accessing Content Blocks
```python
slide_data = state['slides'][0]
for block in slide_data['layout']['content_blocks']:
    if block['type'] == 'text':
        print(f"Text: {block['content'][:50]}...")
    elif block['type'] == 'image_placeholder':
        print(f"Image: {block['image_path']}")
```

### Customizing Parameters
```python
from src.agent.graph import SlideGenerationAgent

agent = SlideGenerationAgent()
result = agent.generate_slides(
    base_text="Machine Learning Fundamentals",
    num_slides=8,
    aspect_ratio="16:9",
    style="creative",
    content_richness="detailed"
)
```

---

These examples demonstrate the complete data flow through the slide generation system.

