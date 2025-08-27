# AI-IT-Path-Finder

A comprehensive AI-powered CV generation and optimization system that creates ATS-friendly resumes using advanced language models and modern web technologies.

## 🚀 Overview

AI-IT-Path-Finder is a full-stack application that combines the power of fine-tuned language models with a modern web interface to generate professional, ATS-optimized CVs. The system consists of:

- **Frontend**: Next.js web application with real-time CV generation and preview
- **Backend**: FastAPI server with fine-tuned language models for CV parsing
- **AI Models**: Custom fine-tuned models for structured CV generation
- **ATS Optimization**: Built-in scoring and optimization tools

## ✨ Features

### Frontend (Next.js Client)
- 🤖 **AI-Powered CV Parsing**: Converts unstructured text to structured JSON
- 📄 **Real-time Preview**: Instant HTML preview of generated CVs
- 📥 **PDF Download**: Professional PDF generation with proper formatting
- 🎨 **Modern UI**: Responsive design with dark/light theme support
- 📊 **ATS Scoring**: Built-in ATS compatibility scoring
- ⚡ **Real-time Processing**: Direct integration with AI backend

### Backend (Python/FastAPI)
- 🧠 **Fine-tuned Models**: Custom language models for CV parsing
- 🔍 **Named Entity Recognition**: Advanced text analysis using spaCy
- 📝 **Multiple Formats**: JSON, Markdown, and PDF output
- 🔐 **Secure API**: FastAPI with proper error handling
- 🌐 **CORS Support**: Cross-origin resource sharing enabled

### AI/ML Components
- 📚 **Model Training**: Jupyter notebooks for model fine-tuning
- 🎯 **Dataset Processing**: Synthetic data generation and preprocessing
- 🔧 **Model Merging**: Advanced model merging techniques
- 📊 **Performance Analysis**: Comprehensive evaluation metrics

## 🏗️ Project Structure

```
AI-IT-Path-Finder/
├── client/                     # Next.js frontend application
│   ├── src/
│   │   ├── app/               # Next.js app router pages
│   │   ├── components/        # React components
│   │   ├── contexts/          # React contexts
│   │   ├── lib/              # Utilities and API clients
│   │   └── types/            # TypeScript type definitions
│   ├── public/               # Static assets
│   └── package.json          # Frontend dependencies
├── PromptingSystem/          # Python backend and AI models
│   ├── ats_friendly_cv_generator.py  # Main CV generator
│   ├── cv_api.py             # FastAPI server
│   ├── final_merged_model_v2/ # Fine-tuned model files
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Backend documentation
├── *.ipynb                   # Jupyter notebooks for ML development
└── README.md                # This file
```

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **UI Components**: Lucide React icons
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.8+
- **AI/ML**: Transformers (Hugging Face), PyTorch
- **NLP**: spaCy for Named Entity Recognition
- **PDF Generation**: ReportLab
- **API**: Groq for language model inference

### AI Models
- **Base Models**: Mistral 7B, Google Gemini
- **Fine-tuning**: Custom training scripts
- **Model Merging**: Advanced merging techniques
- **Evaluation**: Comprehensive metrics and testing

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ (for frontend)
- Python 3.8+ (for backend)
- Google AI Studio API key (free at https://makersuite.google.com/app/apikey)

### Frontend Setup

1. **Navigate to client directory:**
   ```bash
   cd client
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure backend URL:**
   Update `src/lib/config.ts` with your backend URL or set `NEXT_PUBLIC_BACKEND_URL` environment variable.

4. **Start development server:**
   ```bash
   npm run dev
   ```

5. **Open browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Backend Setup

1. **Navigate to PromptingSystem directory:**
   ```bash
   cd PromptingSystem
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Set up API key:**
   ```bash
   cp env_template.txt .env
   # Edit .env and add your Google AI Studio API key
   ```

5. **Start FastAPI server:**
   ```bash
   python cv_api.py
   ```

## 📖 Usage

### Web Interface
1. Navigate to the CV form page
2. Paste your raw CV text into the input area
3. Click "Generate JSON" to create structured data
4. Preview the formatted CV
5. Download as PDF or use ATS scoring

### Command Line
```bash
cd PromptingSystem
python ats_friendly_cv_generator.py
```

### API Endpoints
- `POST /generate-cv-json` - Convert text to structured JSON
- `POST /preview-cv` - Generate HTML preview
- `POST /download-cv` - Create PDF download
- `GET /health` - Health check

## 🔧 Configuration

### Frontend Configuration
Update `client/src/lib/config.ts`:
```typescript
export const config = {
  BACKEND_URL: 'http://localhost:8000', // or your ngrok URL
  // ... other settings
};
```

### Backend Configuration
Set environment variables in `PromptingSystem/.env`:
```
GOOGLE_API_KEY=your_api_key_here
HF_USERNAME=your_huggingface_username
HF_TOKEN=your_huggingface_token_here
```

**⚠️ Security Note**: Never commit API keys or tokens to version control. Use environment variables or `.env` files (which are ignored by git) to store sensitive information.

## 🧪 Development

### Model Training
- Use the Jupyter notebooks for model fine-tuning
- `Mistral_7B_Model_Finetune_ATSCV_Generator_v2.ipynb` - Main training notebook
- `Dataset_preprocess.ipynb` - Data preprocessing
- `generate_synthetic_qa_ba_profiles.py` - Synthetic data generation

### Testing
- Frontend: `npm run lint` for code quality
- Backend: Run individual Python scripts for testing
- API: Use FastAPI's automatic documentation at `/docs`

## 📊 Performance

The system achieves:
- **High Accuracy**: Fine-tuned models for precise CV parsing
- **Fast Processing**: Real-time generation and preview
- **ATS Compatibility**: Optimized formatting for maximum compatibility
- **Scalable Architecture**: Modular design for easy extension

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow TypeScript best practices for frontend
- Use Python type hints for backend code
- Maintain comprehensive documentation
- Test thoroughly before submitting PRs

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google AI Studio for language model access
- Hugging Face for transformer models
- Next.js team for the excellent framework
- FastAPI for the high-performance Python web framework

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the individual README files in `client/` and `PromptingSystem/`
- Review the Jupyter notebooks for detailed implementation

---

**Made with ❤️ for the AI and IT community**