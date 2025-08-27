# ATS-Friendly CV Generator

A standalone Python script that generates professional, ATS-friendly CVs from text input using AI-powered parsing and formatting.

## Features

- 🤖 AI-powered CV text parsing using Google's Gemini model
- 📄 Generates structured JSON data from unstructured CV text
- 📝 Creates both Markdown and PDF formats
- 🔍 Named Entity Recognition using spaCy
- 🔐 Secure API key storage
- 💻 Terminal-based interface for easy input
- 📱 ATS-friendly formatting for maximum compatibility

## Prerequisites

- Python 3.7 or higher
- Google AI Studio API key (free at https://makersuite.google.com/app/apikey)

## Installation

1. **Clone or download the files:**
   ```bash
   # If you have the files locally, just navigate to the directory
   cd /path/to/cv-generator
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install spaCy English model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

## Setup API Key

You have several options to set up your Google AI Studio API key:

### Option 1: .env File (Recommended)
1. Copy the template file:
   ```bash
   cp env_template.txt .env
   ```
2. Edit the `.env` file and replace `your_api_key_here` with your actual API key:
   ```
   GOOGLE_API_KEY=AIzaSyC1234567890abcdefghijklmnopqrstuvwxyz
   ```

### Option 2: Environment Variable
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

### Option 3: Config File (Automatic)
The script will automatically save your API key to `~/.cv_generator_config` on first use.

### Option 4: Manual Input
Enter your API key when prompted by the script.

## Usage

1. **Run the script:**
   ```bash
   python ats_friendly_cv_generator.py
   ```

2. **Follow the prompts:**
   - Enter your Google AI Studio API key (if not already set)
   - Paste your CV text when prompted
   - Press Enter twice when done with CV text
   - Choose a filename for the PDF (or use default)

3. **Get your results:**
   - Structured JSON data (displayed in terminal)
   - Markdown format CV (displayed in terminal)
   - Professional PDF CV (saved to file)

## Example Usage

```bash
$ python ats_friendly_cv_generator.py

🚀 ATS-Friendly CV Generator
==================================================
✅ All required libraries are already installed.
🔑 API Key loaded from environment variable.
✅ spaCy English model loaded.

============================================================
📝 CV TEXT INPUT
============================================================
Please paste your CV text below.
Press Enter twice when you're done:
------------------------------------------------------------
[Paste your CV text here and press Enter twice]

✅ CV text loaded (1234 characters)

--- SpaCy Named Entity Recognition (NER) ---
Entity: 'John Doe', Label: 'PERSON'
Entity: 'Software Engineer', Label: 'WORK_OF_ART'
...
--------------------------------------------

🤖 Step 1: Calling LLM to extract JSON from text...
✅ Successfully generated and parsed JSON from LLM response.

--- ✨ Extracted CV Data (JSON Format) ✨ ---
{
  "personal_info": {
    "name": "John Doe",
    "job_title": "Software Engineer",
    ...
  },
  ...
}

🤖 Step 2: Calling LLM to generate formatted CV from JSON...
✅ Successfully generated formatted CV from JSON.

--- ✨ Generated CV (Markdown Format) ✨ ---
# John Doe
## Software Engineer
...

🚀 Step 3: Starting final PDF generation...
Enter PDF filename (default: John_Doe_CV.pdf): 
✅ PDF 'John_Doe_CV.pdf' generated successfully!
📁 File saved at: /path/to/John_Doe_CV.pdf
```

## Input Format

The script accepts any text format for your CV. Simply paste your CV content when prompted. The AI will automatically:

- Extract personal information (name, contact details, location)
- Identify skills and categorize them
- Parse work experience and responsibilities
- Extract project information
- Identify education details
- Find references and contact information

## Output Files

- **JSON Data**: Structured representation of your CV data
- **Markdown CV**: Clean, ATS-friendly markdown format
- **PDF CV**: Professional PDF with proper formatting and layout

## Troubleshooting

### Common Issues

1. **Missing spaCy model:**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **API key issues:**
   - Make sure your Google AI Studio API key is valid
   - Check that you have sufficient quota/credits

3. **PDF generation errors:**
   - Ensure you have write permissions in the current directory
   - Check that the filename doesn't contain invalid characters

### Error Messages

- `❌ Missing dependency`: Install required packages with `pip install -r requirements.txt`
- `❌ spaCy model not found`: Run `python -m spacy download en_core_web_sm`
- `❌ API key is required`: Set your Google AI Studio API key

## Security Notes

- API keys are stored securely in your home directory (`~/.cv_generator_config`)
- The config file has restricted permissions
- You can delete the config file anytime to remove stored API keys
- Environment variables are the most secure option for API key storage

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve the CV generator. 