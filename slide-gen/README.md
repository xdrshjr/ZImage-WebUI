# Intelligent Slide Generation System

An AI-powered presentation generator that creates visually appealing, content-rich slides from textual input using Python and LangGraph.

## 🎯 Features

- **AI-Driven Content Generation**: Uses LLM to generate structured outlines, layouts, and content
- **Intelligent Image Generation**: Automatically creates relevant images with refined prompts
- **Multiple Template Types**: Three professionally designed templates (Title & Content, Two Column, Image Focus)
- **Multiple Output Formats**: Generates HTML, PNG images, and consolidated PDF
- **Style Customization**: Support for different visual styles (professional, creative, minimal, academic)
- **Flexible Configuration**: Customizable aspect ratios, content richness, and slide count
- **Robust Error Handling**: Graceful degradation with placeholder images and comprehensive logging

## 🏗️ Architecture

The system uses **LangGraph** to orchestrate a multi-phase workflow:

1. **Phase 1: Outline Planning** - Generate structured outline for all slides
2. **Phase 2: Page-by-Page Generation** - For each slide:
   - Generate layout and content
   - Refine image prompts
   - Generate images via API
   - Assemble HTML slide
3. **Phase 3: Final Export** - Export to PNG and compile PDF

## 📋 Requirements

- Python 3.9 or higher
- OpenAI-compatible LLM API access
- Image generation API access
- See `requirements.txt` for full dependencies

## 🚀 Installation

### 1. Clone or Download the Repository

```bash
cd slide-gen
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers (Required for PNG Export)

```bash
playwright install chromium
```

## ⚙️ Configuration

### 1. Create `.env` File

Copy the example configuration:

```bash
cp .env.example .env
```

### 2. Edit `.env` File

Open `.env` and configure your API credentials:

```env
# LLM Configuration
LLM_API_KEY=your-llm-api-key-here
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-4

# Image Generation Configuration
IMAGE_API_KEY=your-image-api-key-here
IMAGE_API_URL=https://your-image-api.com/generate
IMAGE_MODEL=stable-diffusion-xl

# Generation Settings
DEFAULT_TIMEOUT=60
MAX_RETRIES=3
```

**Important**: Replace placeholder values with your actual API credentials.

## 📖 Usage

### Basic Usage

Run the system with hardcoded test parameters:

```bash
python main.py
```

This will generate a 6-slide presentation about "Introduction to Artificial Intelligence and its applications in modern technology".

### Custom Parameters

To customize parameters, edit `main.py`:

```python
params = {
    "base_text": "Your topic here",
    "num_slides": 8,                    # Number of slides (1-50)
    "aspect_ratio": "16:9",             # "16:9", "4:3", or "16:10"
    "style": "professional",            # "professional", "creative", "minimal", "academic"
    "content_richness": "moderate"      # "concise", "moderate", "detailed"
}
```

### Parameter Descriptions

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `base_text` | str | Any text | Source content/topic for slides |
| `num_slides` | int | 1-50 | Total number of slides to generate |
| `aspect_ratio` | str | 16:9, 4:3, 16:10 | Slide dimensions |
| `style` | str | professional, creative, minimal, academic | Visual theme |
| `content_richness` | str | concise, moderate, detailed | Level of content detail |

## 📁 Project Structure

```
slide-gen/
├── README.md                      # This file
├── README-BackendService.md      # Image API documentation
├── .env.example                  # Configuration template
├── .env                          # Your credentials (gitignored)
├── requirements.txt              # Python dependencies
├── main.py                       # Entry point
├── src/
│   ├── agent/
│   │   ├── graph.py              # LangGraph workflow
│   │   ├── nodes.py              # Workflow nodes
│   │   └── state.py              # State schema
│   ├── llm/
│   │   ├── client.py             # LLM API client
│   │   └── prompts.py            # Prompt templates
│   ├── image/
│   │   ├── generator.py          # Image generation
│   │   └── refiner.py            # Prompt refinement
│   ├── templates/
│   │   ├── base.html             # Base template
│   │   ├── title_content.html    # Title & Content
│   │   ├── two_column.html       # Two Column
│   │   └── image_focus.html      # Image Focus
│   ├── renderer/
│   │   ├── html_renderer.py      # HTML generation
│   │   ├── image_exporter.py     # HTML to PNG
│   │   └── pdf_exporter.py       # PDF compilation
│   └── utils/
│       ├── config.py             # Configuration
│       └── validators.py         # Input validation
└── output/                       # Generated files (created automatically)
    ├── html/                     # Individual slide HTML
    ├── images/                   # Generated images
    ├── slide_images/             # Slide PNGs
    └── final_presentation.pdf    # Final PDF
```

## 🎨 Templates

### 1. Title and Content
- Title at top (max 60-70 chars)
- Content area with text blocks
- 1-2 image slots on right
- Best for: Standard content slides

### 2. Two Column
- Title at top
- Left column: Text
- Right column: Text or image
- Best for: Comparisons, lists with visuals

### 3. Image Focus
- Centered large image
- Minimal text (title + caption)
- Best for: Visual storytelling, impactful images

## 📤 Output Files

After successful generation, you'll find:

- **`output/html/`** - Individual HTML files for each slide
- **`output/images/`** - AI-generated images used in slides
- **`output/slide_images/`** - PNG exports of complete slides
- **`output/final_presentation.pdf`** - Multi-page PDF presentation

## 🔧 Troubleshooting

### Issue: "LLM_API_KEY is required in .env file"

**Solution**: Create a `.env` file from `.env.example` and add your API keys.

### Issue: PNG export shows placeholder text

**Solution**: Install Playwright browsers:
```bash
playwright install chromium
```

### Issue: PDF generation fails

**Solution**: 
1. Ensure WeasyPrint dependencies are installed (may require system libraries on Linux)
2. The system will fall back to alternative PDF generation if WeasyPrint fails

### Issue: Image generation fails

**Solution**: 
- Check your `IMAGE_API_KEY` and `IMAGE_API_URL` in `.env`
- Review `README-BackendService.md` for API requirements
- System will use placeholder images if generation fails

### Issue: Module not found errors

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
# Activate venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## 🔍 Example Output

When you run `python main.py`, you'll see progress like:

```
============================================================
INTELLIGENT SLIDE GENERATION SYSTEM
============================================================

============================================================
PHASE 1: Generating outline for 6 slides
============================================================
✓ Outline generated: 6 slides
  Slide 1: Introduction to AI
  Slide 2: Machine Learning Basics
  ...

============================================================
PHASE 2: Slide 1/6
Title: Introduction to AI
============================================================
→ Step 2.1: Generating layout and content
✓ Layout generated: title_and_content template
→ Step 2.2 & 2.3: Generating 1 image(s)
  ✓ Image 1 generated
→ Step 2.4: Rendering HTML
✓ HTML saved: slide_1.html

...

============================================================
PHASE 3: Final Export
============================================================
→ Step 3.1: Exporting slide images
  ✓ Slide 1 exported to PNG
  ...
→ Step 3.2: Generating PDF
  ✓ PDF generated: output/final_presentation.pdf

============================================================
✓ SLIDE GENERATION COMPLETED SUCCESSFULLY
============================================================
```

## 🛡️ Error Handling

The system includes robust error handling:

- **API Failures**: Retries with exponential backoff (up to 3 attempts)
- **Image Generation Failures**: Falls back to placeholder images
- **Text Validation**: Automatically truncates content exceeding character limits
- **Graceful Degradation**: Continues generation even if individual components fail

## 📝 Code Quality

- **Type Hints**: Full Python type annotations
- **Logging**: Comprehensive logging at INFO and DEBUG levels
- **Validation**: Input validation before processing
- **Modularity**: Single-responsibility modules
- **Documentation**: Detailed docstrings and comments

## 🔐 Security Notes

- Never commit `.env` file to version control
- Keep API keys secure and rotate regularly
- Use environment variables for all credentials
- Review API rate limits and costs before large-scale generation

## 🤝 Contributing

This is a standalone project. For modifications:

1. Follow existing code structure
2. Maintain type hints and docstrings
3. Test changes with various input parameters
4. Update documentation as needed

## 📄 License

MIT License - Feel free to use and modify as needed.

## 🆘 Support

For issues related to:
- **LLM API**: Check your OpenAI-compatible API documentation
- **Image API**: See `README-BackendService.md`
- **Dependencies**: Ensure all packages in `requirements.txt` are installed
- **System Errors**: Check logs in console output for detailed error messages

## 🎓 Advanced Usage

### Programmatic Usage

You can import and use the agent in your own Python scripts:

```python
from src.agent.graph import SlideGenerationAgent

agent = SlideGenerationAgent()
result = agent.generate_slides(
    base_text="Your content",
    num_slides=5,
    aspect_ratio="16:9",
    style="professional",
    content_richness="moderate"
)

print(f"PDF: {result['pdf_path']}")
```

### Custom Templates

To add custom templates:

1. Create new HTML template in `src/templates/`
2. Extend `base.html`
3. Use Jinja2 template syntax
4. Update `src/llm/prompts.py` to include new template type

### Custom Styles

Modify CSS in `src/templates/base.html` to add new style classes:

```css
.slide.mystyle {
    background: your-gradient;
    color: your-color;
}
```

---

**Built with ❤️ using Python, LangGraph, and AI**

