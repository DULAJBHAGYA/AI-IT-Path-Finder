# ATS-Compatible CV Generator

A modern, AI-powered CV generator that creates structured, ATS-friendly resumes from unstructured text input.

## Features

- **AI-Powered CV Parsing**: Uses a fine-tuned language model to extract and structure CV information
- **JSON Generation**: Converts raw CV text into structured JSON format
- **PDF Download**: Generates professional PDF resumes
- **ATS Optimization**: Ensures compatibility with Applicant Tracking Systems
- **Modern UI**: Responsive design with dark/light theme support
- **Real-time Processing**: Direct integration with AI backend

## Backend Integration

This frontend integrates with a FastAPI backend that runs a fine-tuned language model for CV parsing. The backend provides:

- `/generate-cv-json` - Converts CV text to structured JSON
- `/preview-cv-json` - Generates HTML preview from JSON
- `/download-cv-pdf` - Creates PDF from CV text
- `/health` - Health check endpoint

## Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ats-cv-generator
```

2. Install dependencies:
```bash
npm install
```

3. Configure the backend URL:
   - Update the `BACKEND_URL` in `src/lib/config.ts` with your ngrok URL
   - Or set the `NEXT_PUBLIC_BACKEND_URL` environment variable

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. **Enter CV Content**: Paste your raw CV text into the text area
2. **Generate JSON**: Click "Generate JSON" to convert text to structured format
3. **Download PDF**: Click "Download PDF" to get a professional PDF resume
4. **ATS Score**: Use the ATS Score feature to optimize your resume

## Backend Requirements

The backend requires:
- Python 3.8+
- FastAPI
- Transformers (Hugging Face)
- PyTorch
- ReportLab
- ngrok (for public access)

## API Endpoints

### Frontend Routes
- `/` - Main CV form
- `/ats-score` - ATS scoring tool
- `/cv-form` - CV input form

### Backend Integration
- `POST /api/generate-cv-json` - Generate structured JSON
- `POST /api/preview-cv` - Preview CV as HTML
- `POST /api/download-cv` - Download CV as PDF

## Configuration

Update the backend URL in `src/lib/config.ts`:

```typescript
export const config = {
  BACKEND_URL: 'https://your-ngrok-url.ngrok-free.app',
  // ... other config
};
```

## Development

### Project Structure
```
src/
├── app/                 # Next.js app router
│   ├── api/            # API routes
│   ├── cv-form/        # CV form page
│   └── ats-score/      # ATS score page
├── components/          # React components
├── contexts/           # React contexts
├── lib/               # Utilities and config
└── types/             # TypeScript types
```

### Key Components
- `CVForm.tsx` - Main CV input and generation interface
- `CVPreview.tsx` - CV preview component
- `ThemeContext.tsx` - Dark/light theme management

## Technologies Used

- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Transformers, PyTorch, ReportLab
- **AI Model**: Fine-tuned language model for CV parsing
- **Deployment**: ngrok for backend tunneling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
