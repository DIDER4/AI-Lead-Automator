# AI Lead Automator

A comprehensive, secure, and modular desktop application for intelligent B2B lead generation and qualification powered by AI and Firecrawl.

![AI LEAD GIF OPTIMIZED](https://github.com/user-attachments/assets/782ad6fc-9f27-4d05-898f-2d5aa3593bf6)

---

## Overview

**Production-ready Python application for AI-powered B2B lead generation and qualification.**

- **Tech Stack**: Streamlit, Firecrawl API, OpenAI/Anthropic, Pandas, Plotly
- **Architecture**: Modular, security-first, enterprise-grade
- **Security Level**: Enterprise-grade with encryption, validation, GDPR compliance

---

## Features

### **Core Functionality**
- ✅ **Web Scraping**: Firecrawl API integration with retry logic
- ✅ **AI Analysis**: OpenAI GPT-4 or Anthropic Claude for lead qualification
- ✅ **Lead Scoring**: 0-100 score with detailed rationale
- ✅ **Email Generation**: Personalized outreach drafts
- ✅ **SMS Generation**: Short message drafts
- ✅ **Bulk Processing**: Multiple URLs with rate limiting
- ✅ **Data Export**: Excel/CSV with GDPR-compliant mode
- ✅ **Knowledge Base (RAG)**: Upload company documents for AI-enhanced analysis

### **RAG & Knowledge Base**
- **Document Upload**: PDF, TXT, DOCX support
- **Semantic Search**: Find relevant context using embeddings (all-MiniLM-L6-v2)
- **Local Vector Database**: ChromaDB for persistent storage
- **Context Injection**: AI uses your company knowledge to personalize outreach
- **Document Management**: Upload, view, delete documents
- **Test Search**: Preview what context AI will retrieve

### **Security Features**
- **Encryption**: Fernet symmetric encryption (256-bit) for API keys
- **Input Validation**: XSS, SQL injection, path traversal prevention
- **Audit Logging**: Comprehensive logs without exposing secrets
- **Key Rotation**: Support for encryption key rotation
- **GDPR**: Personal data redaction for compliance

### **User Interface**
- **Home**: Welcome page with workflow explanation
- **Settings**: Encrypted API key management
- **Profile**: Define ICP and value proposition
- **Knowledge Base**: Upload and manage company documents for RAG
- **Lead Chat**: Single and bulk URL analysis with RAG support
- **Dashboard**: Visual analytics with Plotly charts

---

## Project Structure

```
AI Lead Automator/
│
├── src/                                  # Source code (modular architecture)
│   ├── __init__.py
│   ├── config.py                        # Configuration management
│   │
│   ├── security/                        # Security module
│   │   ├── __init__.py
│   │   ├── encryption.py                # Fernet encryption, key management
│   │   └── validators.py                # Input validation, XSS prevention
│   │
│   ├── api/                             # API client modules
│   │   ├── __init__.py
│   │   ├── firecrawl.py                 # Firecrawl client with retry logic
│   │   ├── openai_client.py             # OpenAI GPT-4 integration
│   │   ├── anthropic_client.py          # Anthropic Claude integration
│   │   └── mock_data.py                 # Mock data generator for test mode
│   │
│   ├── models/                          # Data models
│   │   ├── __init__.py
│   │   ├── lead.py                      # Lead data model with validation
│   │   └── document.py                  # Document data model for Knowledge Base
│   │
│   ├── services/                        # Business logic layer
│   │   ├── __init__.py
│   │   ├── data_manager.py              # Data persistence (JSON)
│   │   ├── lead_analyzer.py             # Orchestrates scraping + AI analysis + RAG
│   │   └── knowledge_base.py            # RAG service (embeddings, vector search)
│   │
│   ├── ui/                              # User interface
│   │   ├── __init__.py
│   │   ├── components/                  # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   └── charts.py                # Plotly charts, UI helpers
│   │   └── pages/                       # Page rendering logic
│   │       ├── __init__.py
│   │       └── ui_pages.py              # All 6 pages (Home, Settings, Profile, KB, Chat, Dashboard)
│   │
│   └── utils/                           # Utility modules
│       ├── __init__.py
│       └── gdpr.py                      # GDPR compliance utilities
│
├── data/                                # Data storage (auto-created)
│   ├── leads_data.json                  # Lead database
│   ├── secret.key                       # Encryption key 
│   ├── config.encrypted                 # Encrypted configuration
│   ├── chroma_db/                       # ChromaDB vector database 
│   │   └── [vector embeddings]          # Persistent vector storage
│   └── documents/                       # Uploaded knowledge base files 
│       ├── documents_metadata.json      # Document metadata tracking
│       └── [uuid]_[filename]            # Stored original files
│
├── logs/                                # Application logs (auto-created)
│   └── app.log                          # Main application log
│
├── tests/                               # Unit tests
│   ├── __init__.py
│   └── test_security.py                 # Security module tests
│
├── app.py                               # Main entry point
├── requirements.txt                     # All dependencies (production + development)
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore rules
└── RAG_IMPLEMENTATION.md                # RAG technical documentation
```

---

## Module Responsibilities

### **`src/config.py`**
- Application configuration management
- Constants and API endpoints
- Logging configuration
- Type-safe `AppConfig` dataclass

### **`src/security/`**
- **`encryption.py`**: Fernet encryption, key management, atomic file operations
- **`validators.py`**: Input validation, XSS prevention, URL/API key validation

### **`src/api/`**
- **`firecrawl.py`**: Web scraping with retry logic and comprehensive error handling
- **`openai_client.py`**: GPT-4o-mini integration for lead analysis with RAG support
- **`anthropic_client.py`**: Claude 3.5 Sonnet as alternative AI provider with RAG support
- **`mock_data.py`**: Centralized mock data generator for test mode

### **`src/models/`**
- **`lead.py`**: Type-safe Lead data model with validation and helper methods
- **`document.py`**: Type-safe Document data model for Knowledge Base files

### **`src/services/`**
- **`data_manager.py`**: JSON-based lead persistence with atomic writes
- **`lead_analyzer.py`**: Orchestrates complete analysis workflow (scrape → RAG → AI → save)
- **`knowledge_base.py`**: RAG service for document ingestion, embeddings, and semantic search

### **`src/ui/`**
- **`components/charts.py`**: Reusable UI components (charts, cards, metrics)
- **`pages/ui_pages.py`**: All 6 page renderers (Home, Settings, Profile, KB, Chat, Dashboard)

### **`src/utils/`**
- **`gdpr.py`**: GDPR compliance utilities (data redaction, safe exports)

---

## Quick Start

### **Installation**

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### **First Run**

```bash
# Launch application
streamlit run app.py
```

### **Initial Setup**

1. **Configure API Keys** (Settings page)
   - Add Firecrawl API key
   - Add AI provider key (OpenAI or Anthropic)
   - Keys are automatically encrypted with Fernet

2. **Set Up Profile** (User Profile page)
   - Enter your company website
   - Define your value proposition
   - Specify your Ideal Customer Profile (ICP)

3. **Test Functionality** (Lead Chat page)
   - Analyze a single lead URL
   - Try bulk processing with multiple URLs

4. **View Results** (Dashboard page)
   - Explore 8 pre-loaded test leads
   - Export data in Excel/CSV format

---

## Test Mode

The application includes a **Test Mode** that allows you to test all functionality without requiring API keys or making real API calls. This is perfect for demonstrations, development, or trying the application before purchasing API subscriptions.

### **How Test Mode Works**

- **Automatic Activation**: Test mode automatically activates when no API keys are configured
- **Mock Data Generation**: Uses realistic but simulated data for both web scraping and AI analysis
- **Consistent Results**: Same URL produces the same mock data (deterministic)
- **UI Indicators**: Blue info boxes show when test mode is active
- **No API Costs**: No API calls are made in test mode

### **Activating Test Mode**

Test mode is enabled automatically when:
- No Firecrawl API key is configured, OR
- No AI provider (OpenAI/Anthropic) API key is configured

**To run in Test Mode:**
1. Simply launch the application without configuring API keys
2. Go directly to Lead Chat page
3. Enter any URL (e.g., `https://example.com`)
4. Click "Analyze Lead" to see mock results

### **Deactivating Test Mode (Going Production)**

To use real API calls and live data:

1. **Go to Settings Page**
2. **Add Firecrawl API Key**
   - Get your key from https://firecrawl.dev
   - Enter key and click "Save API Keys"
3. **Add AI Provider Key**
   - OpenAI: Get key from https://platform.openai.com
   - Anthropic: Get key from https://console.anthropic.com
   - Enter key and click "Save API Keys"
4. **Test Connection** (optional but recommended)
   - Use the "Test Connection" buttons to verify keys work

Once valid API keys are detected, test mode automatically deactivates and real API calls begin.

---

## Knowledge Base & RAG (Retrieval Augmented Generation)

The application includes a powerful **Knowledge Base** feature that allows you to upload company documents and have the AI use this information to create more personalized and accurate lead analysis.

### **How RAG Works**

1. **Document Upload**: Upload PDFs, text files, or Word documents containing:
   - Company information and value propositions
   - Product specifications and features
   - Case studies and success stories
   - Pricing information
   - Competitive advantages

2. **Automatic Processing**:
   - Documents are split into manageable chunks (1000 characters)
   - Each chunk is converted into a vector embedding using semantic analysis
   - Stored in a local ChromaDB database for fast retrieval

3. **Intelligent Context Retrieval**:
   - When analyzing a lead, the system searches your knowledge base
   - Finds the 3 most relevant chunks based on semantic similarity
   - Injects this context into the AI prompt

4. **Enhanced Analysis**:
   - AI generates emails referencing your actual products/services
   - Lead scores consider fit with your documented offerings
   - Outreach is personalized using your company's voice and examples

### **Using the Knowledge Base**

**Upload Documents:**
```
1. Navigate to "Knowledge Base" page
2. Click "Choose a file" and select PDF/TXT/DOCX
3. Click "Upload & Index"
4. Document is automatically chunked and embedded
```

**Manage Documents:**
- View all uploaded documents with metadata
- See chunk count and file size
- Delete documents you no longer need
- Preview document content

**Test Search:**
- Enter a search query to test retrieval
- See what context the AI would receive
- Verify relevant information is being found

**Integration with Lead Analysis:**
- Knowledge Base is automatically used when analyzing leads
- Status shown on Lead Chat page
- No configuration needed - just upload and go!

### **Best Practices**

✅ **Do Upload:**
- Product/service descriptions
- Company mission and values
- Case studies and testimonials
- Pricing sheets and packages
- FAQs and objection handlers

❌ **Don't Upload:**
- Personal customer data (GDPR)
- Confidential internal documents
- Legal contracts or NDAs
- Sensitive financial information

### **Technical Details**

- **Embedding Model**: all-MiniLM-L6-v2 (384 dimensions)
- **Vector Database**: ChromaDB (local, persistent)
- **Chunking**: 1000 chars with 200 char overlap
- **Retrieval**: Top 3 chunks by cosine similarity
- **Storage**: `data/chroma_db/` and `data/documents/`

---

## Performance Metrics

- **Single Lead Analysis**: 5-10 seconds (without KB) / 6-12 seconds (with KB)
  - Scraping: 2-3 seconds
  - AI Analysis: 2-5 seconds
  - KB Search: 1-2 seconds (if KB active)
  - Saving: <1 second

- **Bulk Processing**: ~50 URLs in 8 minutes
  - 1-second rate limit between requests
  - Parallel-ready architecture

- **Memory Usage**: 100-200 MB
- **Disk Usage**: <10 MB (excluding data)

---

## Security Features

### **Enterprise-Grade Protection**

✅ **Encryption**
- API keys encrypted with Fernet (256-bit symmetric encryption)
- Atomic file writes for configuration data
- Support for key rotation

✅ **Input Validation**
- URL validation and sanitization
- XSS prevention (HTML escaping)
- Path traversal protection
- API key format validation
- SQL injection prevention

✅ **GDPR Compliance**
- Personal data redaction utilities
- Export modes: Safe (redacted) / Full (original)
- Data minimization patterns

✅ **Logging**
- No secrets in logs
- API key masking (sk-1234...abcd)
- SHA256 hashes for debugging
- Comprehensive error tracking

✅ **Error Handling**
- Try-catch blocks throughout
- User-friendly error messages
- Graceful degradation

---

## Security Considerations

### **Critical Files (DO NOT SHARE)**
- `data/secret.key` - Fernet encryption key
- `data/config.encrypted` - Encrypted API keys
- `data/chroma_db/` - Vector database (contains embeddings)
- `data/documents/` - Uploaded company documents
- `.env` - Environment variables (if used)

### **Backup Recommendations**
- Copy `data/secret.key` to secure backup location
- Store encrypted config safely
- Backup Knowledge Base: `data/chroma_db/` and `data/documents/`
- Never commit these files to version control

---

## API Usage & Costs

### **Firecrawl**
- **Cost**: ~$0.01-0.05 per page
- **Rate Limit**: Configurable (default: 1 req/sec)
- **Features**: JavaScript rendering, clean markdown output

### **OpenAI GPT-4o-mini**
- **Cost**: ~$0.001 per lead
- **Model**: gpt-4o-mini
- **Response**: Structured JSON

### **Anthropic Claude 3.5 Sonnet**
- **Cost**: ~$0.006 per lead
- **Model**: claude-3-5-sonnet-20241022
- **Response**: Text with JSON extraction

---

## Development

### **Running Tests**
```bash
# Install all dependencies (including development tools)
pip install -r requirements.txt

# Run tests with coverage
pytest tests/ -v --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # Linux/Mac
start htmlcov/index.html  # Windows
```

### **Code Quality**
```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Security scan
bandit -r src/

# Check dependencies for vulnerabilities
safety check
```

### **Development Mode**
```bash
# Run with hot reload
streamlit run app.py --server.runOnSave true
```

---

## Testing

### **Available Tests**
- ✅ Security module (encryption, validation)
- ⏳ API clients (mocked)
- ⏳ Data models (validation)
- ⏳ Services (business logic)

### **Testing Strategy**
```bash
# Unit tests
pytest tests/test_security.py -v

# Integration tests (future)
pytest tests/test_integration.py -v

# Full test suite
pytest tests/ -v --cov=src
```

---

## Documentation

- **README.md**: This file (complete guide with RAG documentation)
- **RAG_IMPLEMENTATION.md**: Technical deep-dive on RAG architecture
- **.env.example**: Environment variables template
- **Inline Documentation**: Comprehensive docstrings in all modules

---

## Troubleshooting

### **Common Issues**

**Module Import Errors**
```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Check Python version (requires 3.9+)
python --version
```

**Encryption Errors**
```bash
# If keys are corrupted, delete and reconfigure
rm data/secret.key data/config.encrypted
streamlit run app.py
# Reconfigure in Settings page
```

**Firecrawl API Errors**
- Check API key validity
- Verify account has credits
- Test connection in Settings page

**Knowledge Base Issues**
```bash
# If ChromaDB fails to load
rm -rf data/chroma_db/
# Restart app and re-upload documents

# If embedding model download fails
# Check internet connection
# Model will auto-download on first run (~80MB)
```

**Memory Issues**
- Close other applications
- Reduce number of uploaded documents
- Restart Streamlit application

---

## Support & Resources

### **Documentation Links**
- **Streamlit**: https://docs.streamlit.io
- **Firecrawl**: https://docs.firecrawl.dev
- **OpenAI**: https://platform.openai.com/docs
- **Anthropic**: https://docs.anthropic.com
- **ChromaDB**: https://docs.trychroma.com
- **LangChain**: https://python.langchain.com/docs

### **Getting Help**
- Check logs in `logs/app.log`
- Run verification script: `python verify.py`
- Review inline documentation in source code
- Read RAG_IMPLEMENTATION.md for technical details

---

## License

This project is proprietary software. All rights reserved.

**Note**: This is a test product developed for demonstration and evaluation purposes. It is not intended for production use without proper review and validation.
