# KELP M&A Automation Pipeline

## 🌊 AI-Powered Investment Teaser Generator

Automatically generates professional investment teaser presentations from company one-pagers using LLMs, web scraping, and data verification.

---

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Setup](#setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The KELP M&A Automation Pipeline is an end-to-end system that transforms company information into investor-ready PowerPoint presentations. It combines:

- **AI-powered content generation** using local LLMs (Ollama) or Gemini API
- **Intelligent web scraping** for market data and company insights
- **Automated slide generation** with domain-specific templates
- **Citation verification** to ensure data accuracy
- **Beautiful GUI** built with Streamlit

### What It Does

**Input**: Company one-pager (Markdown file)  
**Output**: Professional 3-slide investment teaser PPT + citation report

**Slides Generated**:
1. **Business Profile** - Company overview, products, industries, with company image
2. **Financials** - Revenue/EBITDA charts, KPIs, shareholder pie chart
3. **Investment Highlights** - AI-generated investor insights, strengths, opportunities

---

## ✨ Features

### Core Capabilities
- ✅ **Multi-Domain Support**: 8 industry templates (Manufacturing, Technology, Logistics, Consumer, Healthcare, Infrastructure, Chemicals, Automotive)
- ✅ **Smart Web Scraping**: 3-tier fallback system (Playwright → Requests → Guessing) to find company pages
- ✅ **LLM-Generated Insights**: Real investor-grade highlights (not templates)
- ✅ **Shareholder Visualization**: Native PPT pie charts with data labels
- ✅ **Image Pipeline**: Intelligent selection + aspect ratio handling (3:2)
- ✅ **Citation Tracking**: Full source verification with detailed reports
- ✅ **Token Cost Tracking**: USD + INR cost estimates
- ✅ **Streamlit GUI**: User-friendly interface for non-technical users

### Data Processing
- Extracts financial data (revenue, EBITDA, RoCE) from MD files
- Classifies companies into appropriate industry domains
- Scrapes market data (market size, CAGR, trends)
- Generates CAGR, margins, and other calculated metrics
- Verifies all claims against source data

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT GUI / CLI                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
            ┌───────────▼──────────┐
            │   KELP PIPELINE      │
            │   (main.py)          │
            └───────────┬──────────┘
                        │
      ┌─────────────────┼─────────────────┐
      │                 │                 │
┌─────▼────┐     ┌──────▼──────┐   ┌─────▼────────┐
│   Data   │     │   Domain    │   │ Web Scraper  │
│Extractor │     │ Classifier  │   │   (Agent 3)  │
│(Agent 1) │     │  (Agent 2)  │   └──────┬───────┘
└─────┬────┘     └──────┬──────┘          │
      │                 │                 │
      │   ┌─────────────▼─────────────────▼───┐
      └───►    Content Writer (Agent 4)       │
          │  - Slide content generation       │
          │  - LLM-powered insights           │
          └─────────────┬─────────────────────┘
                        │
          ┌─────────────▼──────────────┐
          │ Citation Verifier (Agent 5)│
          └─────────────┬───────────────┘
                        │
          ┌─────────────▼──────────────┐
          │  PPT Assembler (Agent 7)   │
          │  - Image placement         │
          │  - Charts & pie charts     │
          │  - Layout management       │
          └────────────────────────────┘
```

### Agent Breakdown

1. **Data Extractor** (`agents/data_extractor.py`)
   - Parses markdown one-pagers
   - Extracts structured data (business info, financials, SWOT)

2. **Domain Classifier** (`agents/domain_classifier.py`)
   - Classifies companies into 8 industry domains
   - Selects appropriate PPT template

3. **Web Scraper** (`agents/web_scraper.py`)
   - Smart page discovery (3-tier fallback)
   - Market data collection
   - No text truncation

4. **Content Writer** (`agents/content_writer.py`)
   - Generates slide content
   - LLM-powered investor insights
   - Never shortens critical data (products, services)

5. **Citation Verifier** (`agents/citation_verifier.py`)
   - Tracks all claims
   - Verifies against source data
   - Generates citation DOCX report

6. **Image Pipeline** (`agents/image_pipeline.py`)
   - Intelligent image selection by filename
   - Maintains 3:2 aspect ratio
   - Pixel-perfect scaling

7. **PPT Assembler** (`agents/ppt_assembler.py`)
   - Fixed grid layout system
   - Native PPT charts (pie, column)
   - Domain-specific branding

---

## 🚀 Setup

### Prerequisites
- Python 3.8+
- Ollama (for local LLM) OR Gemini API key
- Playwright browsers (for web scraping)

### Step 1: Clone Repository
  
```bash
git clone https://github.com/yourusername/kelp_ma_automation.git
cd kelp_ma_automation
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages**:
- `streamlit` - GUI
- `python-pptx` - PPT generation
- `playwright` - Web scraping
- `beautifulsoup4` - HTML parsing
- `google-generativeai` - Gemini API (optional)
- `requests`, `httpx` - HTTP clients

### Step 3: Install Playwright Browsers

```bash
python -m playwright install chromium
```

### Step 4: Set Up LLM

**Option A: Ollama (Local, Free)**

1. Download Ollama: https://ollama.ai/download
2. Install and run:
   ```bash
   ollama pull phi4-mini:latest
   ```
3. Verify:
   ```bash
   ollama list
   ```

**Option B: Gemini API (Cloud)**

1. Get API key: https://aistudio.google.com/apikey
2. Will enter in GUI or set environment variable:
   ```bash
   set GEMINI_API_KEY=your_key_here
   ```

### Step 5: Add Images (Optional)

Place 3:2 ratio images (e.g., 1200x800px) in `images/` folder:

```
images/
├── technology1.jpg       # Technology domain, slide 1
├── manufacturing_main.jpg
├── office_modern.jpg     # Generic tech office
├── factory_floor.jpg     # Generic manufacturing
└── fallback.png          # Default fallback
```

**Naming convention**: `{domain}{number}.jpg` or `{description}.jpg`

See `images/README.md` for full list.

---

## 📖 Usage

### Option 1: Streamlit GUI (Recommended)

1. **Start the GUI**:
   ```bash
   python -m streamlit run gui/app.py
   ```

2. **Open in browser**: http://localhost:8501

3. **Configure LLM**:
   - Select "Ollama" or "Gemini" in sidebar
   - If Gemini: Enter API key
   - If Ollama: Select model (phi4-mini recommended)

4. **Generate Teaser**:
   - Enter company name
   - Upload one-pager MD file
   - Click "🚀 Generate Investment Teaser"

5. **Download**:
   - PPT file
   - Citation report (DOCX)

### Option 2: Command Line

```bash
python main.py "Company Name" "path/to/onepager.md" --output data/output
```

**Options**:
- `--template path/to/template.pptx` - Custom template
- `--skip-scraping` - Skip web scraping
- `--batch` - Process multiple companies

**Batch mode**:
```bash
python main.py "Batch" "data/input/" --batch --output data/output
```

---

## 📁 Project Structure

```
kelp_ma_automation/
├── agents/
│   ├── data_extractor.py        # Agent 1: Parse MD files
│   ├── domain_classifier.py     # Agent 2: Classify domain
│   ├── web_scraper.py           # Agent 3: Web scraping
│   ├── content_writer.py        # Agent 4: Content generation
│   ├── citation_verifier.py     # Agent 5: Verification
│   ├── ppt_assembler.py         # Agent 7: PPT creation
│   └── image_pipeline.py        # Image handling
│
├── config/
│   ├── domain_templates.py      # Domain-specific configs
│   └── brand_guidelines.py      # Kelp branding
│
├── gui/
│   └── app.py                   # Streamlit interface
│
├── images/                      # Image library
│   ├── fallback.png             # Default image
│   └── README.md                # Image guidelines
│
├── templates/                   # PPT templates (8 domains)
│   ├── manufacturing_template.pptx
│   ├── technology_template.pptx
│   └── ...
│
├── utils/
│   ├── ollama_client.py         # Ollama LLM client
│   ├── token_tracker.py         # Token usage tracking
│   └── ...
│
├── data/
│   ├── input/                   # Input one-pagers
│   └── output/                  # Generated PPTs
│
├── main.py                      # Main pipeline
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

---

## ⚙️ Configuration

### Domain Templates

Edit `config/domain_templates.py` to customize:
- Industry keywords for classification
- Slide structures
- Content priorities

### Branding

Edit `config/brand_guidelines.py` for:
- Colors (PRIMARY, SECONDARY, ACCENT)
- Fonts
- Logo placement

### Ollama Models

Supported models:
- `phi4-mini:latest` (Recommended, fast)
- `llama3.2:latest`
- `qwen2.5:latest`
- `mistral:latest`

Change in GUI sidebar or `utils/ollama_client.py`

---

## 🐛 Troubleshooting

### "Ollama not available"
- Check Ollama is running: `ollama list`
- Restart Ollama service
- Pull model: `ollama pull phi4-mini:latest`

### "Playwright install failed"
```bash
python -m playwright install chromium
```

### "No module named 'google.generativeai'"
```bash
pip install google-generativeai
```

### Image not appearing
- Check image is in `images/` folder
- Verify 3:2 aspect ratio (e.g., 1200x800px)
- Check filename matches domain (e.g., `technology1.jpg`)
- Fallback image (`fallback.png`) will be used if no match

### Pie chart not showing shareholder names
- Ensure shareholder data includes percentages
- Format: "Promoters: 65%", "FII - 20%", etc.

### Empty space on Slide 3
- Check one-pager has SWOT data
- Strengths, Opportunities should have 5+ items
- LLM will generate insights if data available

---

## 📊 Token Usage

Token costs are tracked automatically:

- **Console output**: Shows USD + INR
- **JSON file**: `data/output/{company}/token_usage.json`
  ```json
  {
    "total_tokens": 5420,
    "estimated_cost_usd": 0.542,
    "estimated_cost_inr": 45.26
  }
  ```

Conversion rate: 1 USD = ₹83.5

---

## 🎨 Customization

### Add New Domain Template

1. Create template: `templates/newdomain_template.pptx`
2. Add to `config/domain_templates.py`:
   ```python
   'newdomain': {
       'keywords': ['keyword1', 'keyword2'],
       'color': RGBColor(R, G, B)
   }
   ```
3. Add images: `images/newdomain1.jpg`, etc.

### Modify Slide Layout

Edit `agents/ppt_assembler.py`:
- `LAYOUT` dict for positioning (inches)
- `_build_slide_X` methods for content

---

## 📝 Input Format

One-pager must be Markdown with sections:

```markdown
# Company Name

## Business Description
[Description here]

## Products & Services
- Product 1
- Product 2

## Industries Served
- Industry 1

## Financials
### Revenue (₹ Cr)
- FY23: 150
- FY24: 180

### EBITDA (₹ Cr)
- FY23: 30
- FY24: 40

## SWOT
### Strengths
- Strength 1

### Opportunities
- Opportunity 1

## Key Milestones
- {date: "2024", milestone: "Achievement"}

## Key Shareholders
- Promoters: 65%
- FII: 20%
- Public: 15%
```

See `data/input/` for examples.

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- Streamlit for GUI framework
- python-pptx for PPT generation
- Playwright for web scraping
- Ollama for local LLM inference
- Google Gemini API

---

## 📧 Support

Issues: https://github.com/yourusername/kelp_ma_automation/issues

---

**Built with ❤️ by Kelp M&A Team**
