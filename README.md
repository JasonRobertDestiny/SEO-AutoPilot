# SEO-AutoPilot 🚀

[![PyPI version](https://badge.fury.io/py/pyseoanalyzer.svg)](https://badge.fury.io/py/pyseoanalyzer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**🤖 AI-Powered SEO Analysis & Optimization Platform with Professional Report Generation**

SEO-AutoPilot is an advanced SEO analysis tool that combines traditional SEO auditing with cutting-edge AI analysis. It features a professional web interface, comprehensive report generation, and support for multiple AI providers including Anthropic Claude and SiliconFlow (硅基流动).

![SEO-AutoPilot Dashboard](https://img.shields.io/badge/Dashboard-Live%20Demo-brightgreen)

## ✨ Key Features

### 🔍 **Comprehensive SEO Analysis**
- **Professional SEO Scoring**: Detailed 60-point weighted algorithm analyzing title, description, headings, images, content, and links
- **Real-time Analysis**: Fast analysis with optimized performance (99.76% speed improvement)
- **Multi-format Reports**: Generate reports in HTML, JSON, CSV, and TXT formats
- **Progress Tracking**: Visual progress indicators with step-by-step analysis feedback

### 🤖 **AI-Powered Insights**
- **Multiple AI Providers**: Support for Anthropic Claude and SiliconFlow (硅基流动)
- **Chinese AI Analysis**: Specialized Chinese language optimization with SiliconFlow
- **Entity Optimization**: Advanced analysis for knowledge panel readiness
- **Credibility Assessment**: N-E-E-A-T-T signal analysis for trustworthiness
- **Conversational Search**: Optimization for voice and conversational queries

### 🎨 **Professional Web Interface**
- **Modern Dashboard**: Responsive design with dark/light theme support
- **Real-time Scoring**: Live SEO score updates with professional visualizations
- **Interactive Reports**: Downloadable comprehensive reports with detailed insights
- **Progress Animation**: Smooth progress bars preventing user confusion during analysis

### 🗺️ **XML Sitemap Generation**
- **Standards-compliant**: Generate valid XML sitemaps following search engine guidelines
- **Fast Generation**: Optimized sitemap creation (434s → 1.06s performance improvement)
- **URL Prioritization**: Intelligent URL ranking based on SEO analysis results
- **Download Ready**: Instant download functionality for website deployment

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)  
- [🎯 Web Interface](#-web-interface)
- [🤖 AI Integration](#-ai-integration)
- [📊 Report Generation](#-report-generation)
- [🗺️ Sitemap Generation](#️-sitemap-generation)
- [⚙️ Configuration](#️-configuration)
- [🔧 API Reference](#-api-reference)
- [🧪 Testing](#-testing)
- [🤝 Contributing](#-contributing)

## 🚀 Quick Start

### 1. Install the Package
```bash
pip install pyseoanalyzer
```

### 2. Start the Web Interface
```bash
python -m pyseoanalyzer.api
```

### 3. Access the Dashboard
Open your browser and visit: [http://localhost:5000](http://localhost:5000)

### 4. Analyze Your Website
- Enter your website URL in the dashboard
- Click "Analyze Now" and watch the real-time progress
- Review your SEO score and recommendations
- Download comprehensive reports in multiple formats

### 5. Command Line Usage
```bash
# Basic SEO analysis
python-seo-analyzer https://example.com

# With AI-powered analysis
python-seo-analyzer https://example.com --run-llm-analysis

# Generate HTML report
python-seo-analyzer https://example.com --output-format html

# Include sitemap analysis
python-seo-analyzer https://example.com --sitemap sitemap.xml
```

## 📦 Installation

### Option 1: PyPI Installation (Recommended)
```bash
# Standard installation
pip install pyseoanalyzer

# Development installation
pip install -e .

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Docker Deployment
```bash
# Build and run
docker build -t seo-autopilot .
docker run -p 5000:5000 seo-autopilot

# With environment variables
docker run -p 5000:5000 -e ANTHROPIC_API_KEY="your_key" seo-autopilot
```

### Option 3: Development Setup
```bash
# Clone repository
git clone https://github.com/your-username/SEO-AutoPilot.git
cd SEO-AutoPilot

# Install in development mode
pip install -e .

# Run tests
pytest

# Start development server
python -m pyseoanalyzer.api --debug
```

## 🎯 Web Interface

### Dashboard Features
- **Professional Design**: Modern interface with glassmorphism effects
- **Theme Support**: Complete dark/light theme switching
- **Section Navigation**: Organized tabs for Summary, SEO Analysis, Site Compliance, Links, and Strategy
- **Real-time Updates**: Live progress tracking and score updates

### Analysis Sections
1. **Summary**: Overall SEO score, grade, and critical issues overview
2. **SEO Analysis**: Detailed breakdown of title, description, headings, and content
3. **Site Compliance**: Technical compliance checks and recommendations
4. **Links**: Internal and external link analysis
5. **SEO Strategy**: Actionable tasks and improvement recommendations

### Interactive Features
- **Progress Animation**: Continuous feedback during 1-2 minute AI analysis
- **Score Visualization**: Animated circular progress with color-coded grades
- **Report Downloads**: One-click generation and download of comprehensive reports
- **Sitemap Generation**: Instant XML sitemap creation and download

## 🤖 AI Integration

### Supported AI Providers

#### Anthropic Claude
```bash
# Set environment variable
export ANTHROPIC_API_KEY="your_anthropic_key"

# Run analysis with Claude
python-seo-analyzer https://example.com --run-llm-analysis
```

#### SiliconFlow (硅基流动)
```bash
# Set environment variables
export SILICONFLOW_API_KEY="your_siliconflow_key"
export SILICONFLOW_MODEL="Qwen/Qwen2.5-VL-72B-Instruct"

# Run analysis with SiliconFlow
python-seo-analyzer https://example.com --run-llm-analysis
```

### AI Analysis Features
- **Entity Optimization**: Knowledge panel readiness assessment
- **Credibility Analysis**: Trust signal evaluation and N-E-E-A-T-T scoring
- **Conversational Readiness**: Voice search and conversational query optimization
- **Cross-platform Presence**: Multi-platform visibility analysis
- **Strategic Recommendations**: AI-generated optimization strategies

## 📊 Report Generation

### Supported Formats
- **HTML**: Professional styled reports with interactive elements
- **JSON**: Structured data for programmatic access
- **CSV**: Spreadsheet-compatible format for data analysis
- **TXT**: Plain text reports for simple viewing

### Report Features
- **Executive Summary**: High-level overview with key insights
- **Detailed Metrics**: Comprehensive analysis of all SEO factors
- **Visual Elements**: Charts, graphs, and color-coded sections
- **Actionable Recommendations**: Prioritized improvement suggestions
- **Performance Metrics**: Analysis timing and optimization statistics

### Generate Reports via API
```bash
# HTML report
curl -X POST http://localhost:5000/api/generate-report \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "format": "html"}'

# JSON report  
curl -X POST http://localhost:5000/api/generate-report \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "format": "json"}'
```

## 🗺️ Sitemap Generation

### Features
- **Standards Compliance**: Valid XML sitemaps following search engine guidelines
- **Fast Generation**: Optimized performance with 99.76% speed improvement
- **URL Prioritization**: Intelligent ranking based on SEO analysis results
- **Multiple Formats**: JSON response or direct XML download

### Generate Sitemaps
```bash
# Via API
curl -X POST http://localhost:5000/api/generate-sitemap \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Direct download
curl -X POST http://localhost:5000/api/generate-sitemap \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "format": "download"}' \
  -o sitemap.xml
```

### Web Interface
- Navigate to the SEO Tools section
- Click "Generate & Download Sitemap"
- Automatic download and manual download options available

## ⚙️ Configuration

### Environment Variables
Create a `.env` file with your configuration:

```env
# AI Provider Keys (choose one or both)
ANTHROPIC_API_KEY=your_anthropic_api_key
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_MODEL=Qwen/Qwen2.5-VL-72B-Instruct

# Server Configuration
SEO_ANALYZER_PORT=5000
FLASK_ENV=development

# Optional: Google Integration
GOOGLE_ANALYTICS_VIEW_ID=your_view_id
GOOGLE_SEARCH_CONSOLE_URL=https://your-site.com
```

### Application Settings
- **Port Configuration**: Custom port via `SEO_ANALYZER_PORT` environment variable
- **Debug Mode**: Enable with `FLASK_ENV=development`
- **AI Model Selection**: Configure via `SILICONFLOW_MODEL` for SiliconFlow

## 🔧 API Reference

### Analysis Endpoints
```bash
# Basic SEO analysis
POST /api/analyze
{
  "url": "https://example.com",
  "run_llm_analysis": false
}

# With AI analysis
POST /api/analyze  
{
  "url": "https://example.com",
  "run_llm_analysis": true
}
```

### Report Generation
```bash
# Generate report
POST /api/generate-report
{
  "url": "https://example.com",
  "format": "html",
  "analysis_data": { ... }
}
```

### Sitemap Generation
```bash
# Generate sitemap
POST /api/generate-sitemap
{
  "url": "https://example.com",
  "format": "json"
}
```

### Health Check
```bash
# Check API health
GET /api/health
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_analyzer.py
pytest tests/test_siliconflow_integration.py

# Run with coverage
pytest --cov=pyseoanalyzer --cov-report=html

# Run specific test functions
pytest tests/test_analyzer.py::test_analyze_basic
```

### Test Coverage
- Unit tests for core analysis functionality
- Integration tests for AI providers
- API endpoint testing
- Sitemap generation validation
- Report generation verification

## 🤝 Contributing

### Development Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `pytest`
5. **Run linting**: `ruff check .`
6. **Submit a pull request**

### Development Commands
```bash
# Install development dependencies  
pip install -e .

# Run tests with coverage
pytest --cov=pyseoanalyzer

# Format code
black pyseoanalyzer/
ruff check pyseoanalyzer/

# Build package
python -m build

# Start development server
python -m pyseoanalyzer.api --debug
```

### Code Quality
- **Style**: Follow PEP 8 and use Black for formatting
- **Testing**: Maintain high test coverage
- **Documentation**: Update docs for new features
- **Type Hints**: Use type annotations where appropriate

## 📊 Performance Metrics

### Optimization Achievements
- **Sitemap Generation**: 99.76% faster (434.84s → 1.06s)
- **Analysis Speed**: Optimized processing with parallel operations
- **UI Responsiveness**: Smooth progress tracking during AI analysis
- **Memory Efficiency**: Optimized for large-scale website analysis

### Technical Specifications
- **Python Version**: 3.8+
- **Core Dependencies**: Flask, BeautifulSoup4, trafilatura, aiohttp
- **AI Providers**: Anthropic Claude, SiliconFlow
- **Output Formats**: HTML, JSON, CSV, TXT, XML
- **Architecture**: Modular design with plugin support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AI Providers**: Anthropic for Claude API, SiliconFlow for Chinese AI models
- **Open Source**: Built with ❤️ using open-source libraries
- **Community**: Thanks to all contributors and users
- **SEO Industry**: Inspired by modern SEO best practices and industry standards

---

**SEO-AutoPilot: Professional SEO Analysis with AI-Powered Insights** 🚀

*Built for the modern SEO professional* ⚡