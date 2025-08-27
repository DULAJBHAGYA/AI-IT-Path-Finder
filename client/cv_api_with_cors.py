import json
import os
import re
import io
import torch
import traceback # Import traceback for better error logging
import base64 # For base64 encoding PDF

from fastapi import FastAPI, Form, Response
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware  # Add CORS import

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from textblob import TextBlob

# Hugging Face imports for LLM
from transformers import AutoModelForCausalLM, AutoTokenizer

# Define the FastAPI app
app = FastAPI(
    title="ATS-Friendly CV Generator API",
    description="API to generate structured CV data, Markdown, and PDF from unstructured text using a fine-tuned LLM.",
    version="2.5.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load the local fine-tuned model and tokenizer
MODEL_PATH = "/content/drive/MyDrive/llm-cv-parser-v2/final_merged_model_v2"

model = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    try:
        print(f"Attempting to load model from: {MODEL_PATH}")
        # local_files_only=True ensures it doesn't try to download from Hugging Face Hub
        tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float16,
            device_map="auto",
            local_files_only=True # Important
        )
        model.eval() # Set to evaluation mode
        print("Local fine-tuned model and tokenizer loaded successfully.")
    except Exception as e:
        print(f"Error loading local model during startup: {e}")
        # Ensure model and tokenizer are None if loading fails
        model = None
        tokenizer = None
        # Raise an exception to prevent the app from starting if model isn't loaded
        raise RuntimeError(f"Model loading failed: {e}")


def build_prompt(cv_text: str) -> str:
    return f"""<|system|>You are an expert resume parser that extracts information from CV text and returns it as JSON.</s>
<|user|>{cv_text}</s>
<|assistant|>"""

def generate_llm_response(cv_text: str, max_new_tokens: int = 8000) -> str:
    """Generates initial raw output from the local fine-tuned model."""
    if model is None or tokenizer is None:
        raise RuntimeError("LLM model or tokenizer not loaded. Cannot generate response.")

    prompt = build_prompt(cv_text)
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device) # Add truncation

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    # Decode only the generated part after the prompt
    # Find the start of the assistant's response to avoid re-decoding the prompt
    decoded_full_output = tokenizer.decode(output[0], skip_special_tokens=False) # Keep special tokens for split
    assistant_prefix = "<|assistant|>"
    if assistant_prefix in decoded_full_output:
        response_text = decoded_full_output.split(assistant_prefix)[-1].strip()
    else:
        # Fallback if assistant prefix isn't found (shouldn't happen with proper prompt)
        response_text = tokenizer.decode(output[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()

    # Clean up any residual special tokens that might be left if skip_special_tokens was false
    response_text = response_text.replace("</s>", "").replace("<unk>", "").strip()

    return response_text

def extract_and_fix_json(raw_text):
    """
    Specifically extracts JSON from a string potentially wrapped in 'raw_output': '...'
    and applies specific fixes. This is the version you provided for explicit use.
    """
    print("Attempting JSON extraction and basic fixes (your provided function)...")
    match = re.search(r"'raw_output':\s*'(.*?)'\s*$", raw_text.strip(), re.DOTALL)
    if not match:
        print("Could not find 'raw_output' wrapper. Treating input as direct JSON string.")
        json_str = raw_text.strip()
    else:
        json_str = match.group(1)
        print("Found and extracted content from 'raw_output' wrapper.")

    # Apply fixes from your provided function
    json_str = re.sub(r'("phone":\s*"\+94\s*\d{2}\s*\d{3}\s*\d{4})(,)\s*"email":', r'\1", "email":', json_str)
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)

    braces_diff = json_str.count('{') - json_str.count('}')
    brackets_diff = json_str.count('[') - json_str.count(']')

    json_str += '}' * braces_diff
    json_str += ']' * brackets_diff

    try:
        parsed_json = json.loads(json_str)
        print("Successfully extracted and parsed JSON after basic fixes.")
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"JSON decode error after basic fixes: {e}")
        raise ValueError(f"Could not parse JSON after basic fixes: {e}") # Raise ValueError to indicate failure


# Consolidated the robust parsing logic into one main function.
# This function will be the only custom parser.
def convert_raw_output_to_json(raw_output_from_llm: str) -> dict:
    """
    Convert raw LLM output to valid JSON format using custom extraction and fixing.
    This is the primary JSON parsing pipeline without external API calls.
    """
    print("Converting raw output to JSON using custom robust method...")
    print(f"--- Raw Output (first 500 chars) ---")
    print(raw_output_from_llm[:500] + "..." if len(raw_output_from_llm) > 500 else raw_output_from_llm)

    # First attempt: Try to parse directly (if it's already perfect JSON)
    try:
        parsed_json = json.loads(raw_output_from_llm)
        print("Raw output was already valid JSON, no custom fixing needed.")
        return parsed_json
    except json.JSONDecodeError:
        pass # If direct parsing fails, proceed to custom extraction and fixing

    # Second attempt: Use the custom extract_and_fix_json function
    try:
        parsed_json = extract_and_fix_json(raw_output_from_llm) # Calling your specified fixer
        print(f"--- Converted JSON (formatted) ---")
        print(json.dumps(parsed_json, indent=2)[:1000] + "..." if len(json.dumps(parsed_json, indent=2)) > 1000 else json.dumps(parsed_json, indent=2))
        return parsed_json
    except (ValueError, json.JSONDecodeError) as e:
        print(f"All custom JSON parsing attempts failed: {e}. No further fallback.")
        raise json.JSONDecodeError(f"All custom parsing attempts failed: {e}", raw_output_from_llm, 0)
    except Exception as e:
        print(f"An unexpected error occurred during custom conversion: {e}")
        raise json.JSONDecodeError(f"Unexpected error during custom parsing: {e}", raw_output_from_llm, 0)

def flatten_cv_json(cv_json: dict) -> dict:
    """
    Standardizes the JSON structure, moving potentially mis-nested fields
    and ensuring all expected top-level keys exist.
    """
    if 'skills' in cv_json and isinstance(cv_json['skills'], list):
        if cv_json['skills'] and isinstance(cv_json['skills'][0], str):
            cv_json['skills'] = [{"category": "Technical Skills", "items": cv_json['skills']}]
    if 'tools' in cv_json and isinstance(cv_json['tools'], list):
        if 'skills' not in cv_json: cv_json['skills'] = []
        cv_json['skills'].append({"category": "Tools & Technologies", "items": cv_json['tools']})
        del cv_json['tools']
    if 'experience' in cv_json and isinstance(cv_json['experience'], list) and len(cv_json['experience']) > 0:
        exp0 = cv_json['experience'][0]
        for key in ['projects', 'education', 'volunteering_and_leadership', 'references']:
            if key in exp0 and key not in cv_json:
                cv_json[key] = exp0[key]
                if key in exp0: del exp0[key]
    for key in ['name', 'job_title', 'contact', 'profile_summary', 'skills', 'experience', 'projects', 'education', 'volunteering_and_leadership', 'references']:
        if key not in cv_json:
            if key in ['name', 'job_title', 'profile_summary']: cv_json[key] = ""
            elif key == 'contact': cv_json[key] = {}
            else: cv_json[key] = []
    if 'references' in cv_json and isinstance(cv_json['references'], list):
        for i, ref in enumerate(cv_json['references']):
            # Ensure contact is a dictionary before trying to access keys
            if 'contact' in ref and isinstance(ref['contact'], dict):
                if 'phone' in ref['contact']: cv_json['references'][i]['phone'] = ref['contact']['phone']
                if 'email' in ref['contact']: cv_json['references'][i]['email'] = ref['contact']['email']
                del cv_json['references'][i]['contact']
            # If phone or email are directly at top-level of reference, move them to the new structure if not already there
            if 'phone' in ref and 'phone' not in cv_json['references'][i]: cv_json['references'][i]['phone'] = ref['phone']
            if 'email' in ref and 'email' not in cv_json['references'][i]: cv_json['references'][i]['email'] = ref['email']

    return cv_json

def add_word_spacing(text: str) -> str:
    # Use raw strings for regex patterns
    text = re.sub(r',([^\s])', r', \1', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def draw_justified_paragraph(c: canvas.Canvas, text: str, x: float, y: float, width: float, font_name: str, font_size: float, line_height: float, indent: float = 0, extra_word_space: float = 0) -> float:
    from reportlab.pdfbase.pdfmetrics import stringWidth # Needs to be imported here if not global
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontName = font_name
    style.fontSize = font_size
    style.leading = line_height
    style.alignment = 4 # TA_JUSTIFY
    style.firstLineIndent = indent
    if not text.strip(): return y - line_height
    words = text.split()
    if not words: return y - line_height # Handle empty words list
    lines = []; current_line = []; current_width = 0; space_width = stringWidth(' ', font_name, font_size)
    for word in words:
        word_len = stringWidth(word, font_name, font_size);
        test_width = current_width + word_len + (space_width if current_line else 0) # Only add space if not first word
        if test_width > width and current_line: # If adding this word exceeds width and line is not empty
            lines.append(' '.join(current_line));
            current_line = [word];
            current_width = word_len;
        else:
            current_line.append(word);
            current_width += word_len + space_width; # Add space after word
    if current_line: lines.append(' '.join(current_line)) # Add last line

    for i, line_text in enumerate(lines):
        current_draw_x = x + (indent if i == 0 else 0) # Apply first line indent
        line_word_count = len(line_text.split())

        if i == len(lines) - 1 or line_word_count == 1: # Last line or single word line, left align
            c.drawString(current_draw_x, y, line_text)
        else: # Justify line
            text_width = stringWidth(line_text, font_name, font_size);
            if line_word_count > 1:
                # Calculate extra space needed for justification
                extra_space_per_gap = (width - text_width) / (line_word_count - 1)
            else:
                extra_space_per_gap = 0 # Should not happen for mult-word lines

            word_parts = line_text.split(' ')
            for j, word in enumerate(word_parts):
                c.drawString(current_draw_x, y, word)
                current_draw_x += stringWidth(word, font_name, font_size)
                if j < line_word_count - 1: # Add space after word, except for the last word
                    current_draw_x += (space_width + extra_space_per_gap + extra_word_space)
        y -= line_height
    return y


def create_styled_cv_from_json(data: dict, file_buffer: io.BytesIO) -> io.BytesIO:
    c = canvas.Canvas(file_buffer, pagesize=A4); width, height = A4
    left_margin = 0.5 * inch; right_margin = width - 0.5 * inch; top_margin = height - 0.5 * inch; bottom_margin = 0.5 * inch; content_width = width - 1 * inch
    y_pos = top_margin; x_pos = left_margin; page_count = 1

    # Header Section
    name = data.get('name', 'Your Name'); job_title = data.get('job_title', 'Job Title'); contact_info = data.get('contact', {})
    email = contact_info.get('email', ''); phone = contact_info.get('phone', ''); location = contact_info.get('location', ''); linkedin = contact_info.get('linkedin', ''); github = contact_info.get('github', ''); website = contact_info.get('website', '')
    c.setFont('Helvetica-Bold', 18); c.drawCentredString(width / 2.0, y_pos, name); y_pos -= 18
    if job_title: c.setFont('Helvetica', 12); c.drawCentredString(width / 2.0, y_pos, job_title); y_pos -= 15
    contact_parts = [part for part in [email, phone, location, linkedin, github, website] if part]; contact_line = " | ".join(contact_parts)
    if contact_line: c.setFont('Helvetica', 10); c.drawCentredString(width / 2.0, y_pos, contact_line); y_pos -= 15
    max_text_width = max(c.stringWidth(name, 'Helvetica-Bold', 18), c.stringWidth(job_title, 'Helvetica', 12), c.stringWidth(contact_line, 'Helvetica', 10) if contact_line else 0)
    line_margin = 20; line_x_start = (width - max_text_width) / 2 - line_margin; line_x_end = (width + max_text_width) / 2 + line_margin; line_y = y_pos + 5; c.setLineWidth(0.5); c.line(line_x_start, line_y, line_x_end, line_y); y_pos = line_y - 15

    # Profile Summary
    summary_text = data.get('profile_summary', ''); c.setFont('Helvetica', 10)
    # Check if TextBlob is available before using it
    if 'TextBlob' in globals() and TextBlob is not None:
        try:
            summary_text_corrected = str(TextBlob(summary_text).correct())
        except Exception as e:
            print(f"TextBlob correction failed for summary: {e}. Using original text.")
            summary_text_corrected = summary_text
    else: summary_text_corrected = summary_text
    summary_text_corrected = add_word_spacing(summary_text_corrected); y_pos = draw_justified_paragraph(c, summary_text_corrected, x_pos, y_pos, content_width, 'Helvetica', 10, 12, indent=0); y_pos -= 5

    # Page break check
    if y_pos < bottom_margin + 50:
        c.showPage()
        y_pos = top_margin
        page_count += 1
        if page_count > 2: # Limit to 2 pages
            c.save()
            return file_buffer

    # Skills Section
    skills = data.get('skills', []);
    if skills:
        c.setFont('Helvetica-Bold', 12); c.drawString(x_pos, y_pos, 'SKILLS'); y_pos -= 20
        for skill_cat in skills:
            c.setFont('Helvetica-Bold', 11); c.drawString(x_pos, y_pos, skill_cat.get('category', '')); y_pos -= 15
            c.setFont('Helvetica', 10); skills_list = skill_cat.get('items', []); skills_text = ", ".join(skills_list);
            # Simple text wrapping for skills list
            current_line = ""
            for i, word in enumerate(skills_text.split(', ')): # Split by ', ' to keep phrases intact
                if i > 0: test_line = current_line + ", " + word # Add comma for subsequent items
                else: test_line = current_line + word
                if c.stringWidth(test_line, 'Helvetica', 10) <= content_width:
                    current_line = test_line
                else:
                    if current_line: c.drawString(x_pos, y_pos, current_line.strip()); y_pos -= 12
                    current_line = word # Start new line with the current word
            if current_line: c.drawString(x_pos, y_pos, current_line.strip()); y_pos -= 15
    y_pos -= 10;

    # Page break check
    if y_pos < bottom_margin + 50:
        c.showPage()
        y_pos = top_margin
        page_count += 1
        if page_count > 2:
            c.save()
            return file_buffer

    # Work Experience Section
    experience = data.get('experience', []);
    if experience:
        c.setFont('Helvetica-Bold', 12); c.drawString(x_pos, y_pos, 'WORK EXPERIENCE'); y_pos -= 20
        for job in experience:
            c.setFont('Helvetica-Bold', 11); title_line = f"{job.get('title', '')}, {job.get('company', '')}"; c.drawString(x_pos, y_pos, title_line); y_pos -= 15
            c.setFont('Helvetica', 10); c.drawString(x_pos, y_pos, job.get('duration', '')); y_pos -= 15
            responsibilities = job.get('responsibilities', []);
            for resp in responsibilities:
                resp_text = resp.strip();
                if 'TextBlob' in globals() and TextBlob is not None:
                    try:
                        resp_text = str(TextBlob(resp_text).correct())
                    except Exception as e:
                        print(f"TextBlob correction failed for responsibility: {e}. Using original text.")
                        pass # Continue with original text if correction fails
                resp_text = re.sub(r'\s*\([^)]*\)', '', resp_text).strip(); # Remove text in parentheses
                if len(resp_text) > 150: resp_text = resp_text[:147] + "..." # Truncate long responsibilities
                y_pos_after_draw = draw_justified_paragraph(c, "• " + resp_text, x_pos, y_pos, content_width, 'Helvetica', 10, 12, indent=0)
                y_pos = y_pos_after_draw # Update y_pos based on paragraph drawing
                if y_pos < bottom_margin + 30: # Check for page break after each responsibility
                    c.showPage()
                    y_pos = top_margin
                    page_count += 1
                if page_count > 2:
                    c.save()
                    return file_buffer
            y_pos -= 15;

    # Page break check
    if y_pos < bottom_margin + 50:
        c.showPage()
        y_pos = top_margin
        page_count += 1
        if page_count > 2:
            c.save()
            return file_buffer

    # Projects Section
    projects = data.get('projects', []);
    if projects and page_count <= 2:
        c.setFont('Helvetica-Bold', 12); c.drawString(x_pos, y_pos, 'PROJECTS'); y_pos -= 20;
        for proj in projects:
            c.setFont('Helvetica-Bold', 10); project_title = proj.get('name', '');
            if proj.get('role'): project_title += f" - {proj.get('role', '')}";
            c.drawString(x_pos, y_pos, project_title); y_pos -= 12;

            c.setFont('Helvetica', 10); desc = proj.get('description', '');
            if 'TextBlob' in globals() and TextBlob is not None:
                try:
                    desc = str(TextBlob(desc).correct());
                except Exception as e:
                    print(f"TextBlob correction failed for project description: {e}. Using original text.")
                    pass
            desc = add_word_spacing(desc); desc = desc.replace('\n', ' ').strip();
            y_pos = draw_justified_paragraph(c, desc, x_pos, y_pos, content_width, 'Helvetica', 10, 12, indent=0, extra_word_space=2);

            if proj.get('technologies'):
                tech_line = "Technologies: " + ", ".join(proj.get('technologies', [])); c.setFont('Helvetica', 9);
                # Simple text wrapping for tech list
                current_line = ""
                for i, word in enumerate(tech_line.split(', ')):
                    if i > 0: test_line = current_line + ", " + word
                    else: test_line = current_line + word
                    if c.stringWidth(test_line, 'Helvetica', 9) <= content_width:
                        current_line = test_line
                    else:
                        if current_line: c.drawString(x_pos, y_pos, current_line.strip()); y_pos -= 10
                        current_line = word
                if current_line: c.drawString(x_pos, y_pos, current_line.strip()); y_pos -= 10
            y_pos -= 15;
            if y_pos < bottom_margin + 30:
                c.showPage()
                y_pos = top_margin
                page_count += 1
            if page_count > 2:
                c.save()
                return file_buffer;

    # Education Section
    education = data.get('education', []);
    if education:
        c.setFont('Helvetica-Bold', 12); c.drawString(x_pos, y_pos, 'EDUCATION'); y_pos -= 15;
        for edu in education:
            c.setFont('Helvetica-Bold', 10); degree = edu.get('degree', ''); c.drawString(x_pos, y_pos, degree); y_pos -= 10;
            c.drawString(x_pos, y_pos, edu.get('institution', '')); y_pos -= 10; c.setFont('Helvetica', 10);
            if edu.get('details'): c.drawString(x_pos, y_pos, edu.get('details', '')); y_pos -= 10;
            if edu.get('duration'): c.drawString(x_pos, y_pos, edu.get('duration', '')); y_pos -= 10;
            y_pos -= 10;

    # Volunteering & Leadership Section
    volunteering = data.get('volunteering_and_leadership', []);
    if volunteering and page_count <= 2:
        if y_pos < bottom_margin + 50:
            c.showPage()
            y_pos = top_margin
            page_count += 1
        if page_count > 2:
            c.save()
            return file_buffer;
        c.setFont('Helvetica-Bold', 12); c.drawString(x_pos, y_pos, 'VOLUNTEERING & LEADERSHIP'); y_pos -= 15;
        c.setFont('Helvetica', 10);
        for vol in volunteering[:5]: # Limit to first 5 for conciseness in PDF
            vol_text = vol;
            if len(vol_text) > 100: vol_text = vol_text[:97] + "..."; # Truncate
            y_pos_after_draw = draw_justified_paragraph(c, "• " + vol_text, x_pos, y_pos, content_width, 'Helvetica', 10, 12, indent=0)
            y_pos = y_pos_after_draw
        y_pos -= 10;

    # References Section
    references = data.get('references', []);
    if references and page_count <= 2 and y_pos > bottom_margin + 50:
        c.setFont('Helvetica-Bold', 12); c.drawString(x_pos, y_pos, 'REFERENCES'); y_pos -= 15;
        for ref in references[:2]: # Limit to first 2 references
            ref_phone = ref.get('phone', ''); ref_email = ref.get('email', '');
            if 'contact' in ref and isinstance(ref['contact'], dict): # Handle old 'contact' sub-dict if present
                ref_phone = ref['contact'].get('phone', ref_phone);
                ref_email = ref['contact'].get('email', ref_email);
            c.setFont('Helvetica-Bold', 10); c.drawString(x_pos, y_pos, ref.get('name', '')); y_pos -= 10;
            c.setFont('Helvetica', 10); c.drawString(x_pos, y_pos, ref.get('title', '')); y_pos -= 10;
            if ref_phone: c.drawString(x_pos, y_pos, ref_phone); y_pos -= 10;
            if ref_email: c.drawString(x_pos, y_pos, ref_email); y_pos -= 10;
            y_pos -= 15;

    c.save(); # Finalize PDF drawing
    return file_buffer;


# --- FastAPI Endpoints ---

@app.post("/generate-cv-json", summary="Parse CV text and return structured JSON")
async def generate_cv_json_endpoint(cv_text: str = Form(...)):
    print(f"Received CV text (length: {len(cv_text)})")

    if not cv_text.strip():
        print("Empty CV text received")
        return JSONResponse(status_code=400, content={"error": "CV text cannot be empty."})

    # Ensure model is loaded before attempting inference
    if model is None or tokenizer is None:
        print("Model or tokenizer not loaded. Attempting to load now.")
        try:
            # Call the startup function explicitly if not loaded
            await load_model()
            if model is None or tokenizer is None: # Re-check after attempting load
                 return JSONResponse(status_code=500, content={"error": "Model failed to load. Please check server startup logs."})
        except RuntimeError as e:
            return JSONResponse(status_code=500, content={"error": f"Model failed to load during request: {e}"})


    raw_output = "N/A" # Initialize raw_output for error reporting consistency
    try:
        print("Starting LLM response generation...")
        raw_output = generate_llm_response(cv_text) # This is the initial raw string from the LLM.
        print("--- Raw Output from Local LLM ---")
        print(raw_output[:1000] + "..." if len(raw_output) > 1000 else raw_output)

        print("Converting raw output to JSON...")
        # The convert_raw_output_to_json function handles all the robust extraction and repair.
        # The result (converted_json) is the "fixed raw_output" as a Python dictionary.
        converted_json = convert_raw_output_to_json(raw_output)

        print("Flattening JSON structure...")
        final_json = flatten_cv_json(converted_json) # Further standardizes the structure

        print("--- Final Processed JSON ---")
        print(json.dumps(final_json, indent=2)[:1000] + "..." if len(json.dumps(final_json, indent=2)) > 1000 else json.dumps(final_json, indent=2))

        return {"json": final_json, "success": True}
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError after all attempts: {e}")
        return JSONResponse(status_code=500, content={
            "error": f"Failed to parse JSON: {e}", # Updated message
            "raw_output": raw_output[:500] + "..." if len(raw_output) > 500 else raw_output,
            "success": False
        })
    except Exception as e:
        print(f"General error in generate_cv_json_endpoint: {e}")
        traceback.print_exc() # Print full traceback for debugging
        return JSONResponse(status_code=500, content={
            "error": str(e),
            "raw_output": raw_output[:500] + "..." if len(raw_output) > 500 else raw_output,
            "success": False
        })

@app.post("/preview-cv-json", summary="Display structured CV JSON in an HTML formatted view")
async def preview_cv_json_endpoint(cv_json: str = Form(...)):
    try:
        print("------")
        data = json.loads(cv_json)
        html_content = f"<!DOCTYPE html><html><head><title>CV JSON Preview</title><style>body {{ font-family: monospace; white-space: pre-wrap; }}</style></head><body><pre>{json.dumps(data, indent=4)}</pre></body></html>"
        return HTMLResponse(content=html_content)
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"error": "Invalid JSON format."})
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-cv-markdown", summary="Generate CV in Markdown format from text")
async def generate_cv_markdown_endpoint(cv_text: str = Form(...)):
    if not cv_text.strip():
        return JSONResponse(status_code=400, content={"error": "CV text cannot be empty."})
    if model is None or tokenizer is None:
        print("Model or tokenizer not loaded for Markdown generation. Attempting to load now.")
        try:
            await load_model()
            if model is None or tokenizer is None:
                 return JSONResponse(status_code=500, content={"error": "Model failed to load. Please check server startup logs."})
        except RuntimeError as e:
            return JSONResponse(status_code=500, content={"error": f"Model failed to load during request: {e}"})

    raw_output = "N/A"
    try:
        raw_output = generate_llm_response(cv_text)
        # Here, converted_json is the "fixed raw_output" as a Python dictionary.
        converted_json = convert_raw_output_to_json(raw_output)
        cv_json = flatten_cv_json(converted_json)
        # Fix markdown newlines if they're escaped as \\n
        md = f"# {cv_json.get('name', 'CV')}\n\n"
        if cv_json.get('job_title'): md += f"## {cv_json['job_title']}\n\n"
        if cv_json.get('contact'):
            md += "### Contact\n"
            for k, v in cv_json['contact'].items():
                if v: md += f"- **{k.replace('_', ' ').title()}**: {v}\n"
            md += "\n"
        if cv_json.get('profile_summary'): md += f"### Summary\n{cv_json['profile_summary']}\n\n"
        if cv_json.get('skills'):
            md += "### Skills\n"
            for category in cv_json['skills']:
                md += f"- **{category.get('category', 'Category')}**: {', '.join(category.get('items', []))}\n"
            md += "\n"
        if cv_json.get('experience'):
            md += "### Experience\n"
            for exp in cv_json['experience']:
                md += f"- **{exp.get('title', '')}** at {exp.get('company', '')} ({exp.get('duration', '')})\n"
                for resp in exp.get('responsibilities', []): md += f"  - {resp}\n"
            md += "\n"
        if cv_json.get('education'):
            md += "### Education\n"
            for edu in cv_json['education']:
                md += f"- **{edu.get('degree', '')}** from {edu.get('institution', '')} ({edu.get('duration', '')})\n"
                if edu.get('details'): md += f"  - {edu.get('details')}\n"
            md += "\n"
        return {"markdown": md}
    except Exception as e:
        print(f"Error in Markdown generation: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/download-cv-pdf", summary="Generate and Download CV as PDF")
async def download_cv_pdf_endpoint(cv_text: str = Form(...)):
    if not cv_text.strip():
        return JSONResponse(status_code=400, content={"error": "CV text cannot be empty."})
    if model is None or tokenizer is None:
        print("Model or tokenizer not loaded for PDF generation. Attempting to load now.")
        try:
            await load_model()
            if model is None or tokenizer is None:
                 return JSONResponse(status_code=500, content={"error": "Model failed to load. Please check server startup logs."})
        except RuntimeError as e:
            return JSONResponse(status_code=500, content={"error": f"Model failed to load during request: {e}"})

    raw_output = "N/A"
    try:
        raw_output = generate_llm_response(cv_text)
        # Here, converted_json is the "fixed raw_output" as a Python dictionary.
        converted_json = convert_raw_output_to_json(raw_output)
        cv_json = flatten_cv_json(converted_json)
        pdf_buffer = io.BytesIO()
        create_styled_cv_from_json(cv_json, pdf_buffer)
        pdf_buffer.seek(0)
        name = cv_json.get("name", "cv").replace(" ", "_")
        filename = f"{name}_CV.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        print(f"Error in PDF generation: {e}")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/test-raw-conversion", summary="Test raw output conversion and CV generation (for debugging)")
async def test_raw_conversion_endpoint(raw_text: str = Form(...)):
    """
    Test endpoint to convert raw LLM output to JSON, then generate Markdown and PDF.
    Useful for debugging the full pipeline from raw output to CV.
    """
    try:
        print("=== Testing Raw Output Conversion and CV Generation ===")
        # 1. Convert raw output to valid JSON
        converted_json = convert_raw_output_to_json(raw_text)
        flattened_json = flatten_cv_json(converted_json)

        # 2. Generate Markdown from the flattened JSON
        md = f"# {flattened_json.get('name', 'CV')}\n\n"
        if flattened_json.get('job_title'): md += f"## {flattened_json['job_title']}\n\n"
        if flattened_json.get('contact'):
            md += "### Contact\n"
            for k, v in flattened_json['contact'].items():
                if v: md += f"- **{k.replace('_', ' ').title()}**: {v}\n"
            md += "\n"
        if flattened_json.get('profile_summary'): md += f"### Summary\n{flattened_json['profile_summary']}\n\n"
        if flattened_json.get('skills'):
            md += "### Skills\n"
            for category in flattened_json['skills']:
                md += f"- **{category.get('category', 'Category')}**: {', '.join(category.get('items', []))}\n"
            md += "\n"
        if flattened_json.get('experience'):
            md += "### Experience\n"
            for exp in flattened_json['experience']:
                md += f"- **{exp.get('title', '')}** at {exp.get('company', '')} ({exp.get('duration', '')})\n"
                for resp in exp.get('responsibilities', []): md += f"  - {resp}\n"
            md += "\n"
        if flattened_json.get('education'):
            md += "### Education\n"
            for edu in flattened_json['education']:
                md += f"- **{edu.get('degree', '')}** from {edu.get('institution', '')} ({edu.get('duration', '')})\n"
                if edu.get('details'): md += f"  - {edu.get('details')}\n"
            md += "\n"
        # Add other sections if desired (projects, volunteering, references)
        if flattened_json.get('projects'):
            md += "### Projects\n"
            for proj in flattened_json['projects']:
                md += f"- **{proj.get('name', '')}** ({proj.get('role', '')})\n"
                if proj.get('description'): md += f"  - {proj.get('description')}\n"
                if proj.get('technologies'): md += f"  - Technologies: {', '.join(proj.get('technologies', []))}\n"
            md += "\n"
        if flattened_json.get('volunteering_and_leadership'):
            md += "### Volunteering & Leadership\n"
            for vol in flattened_json['volunteering_and_leadership']: md += f"- {vol}\n"
            md += "\n"
        if flattened_json.get('references'):
            md += "### References\n"
            for ref in flattened_json['references']:
                md += f"- {ref.get('name', '')}, {ref.get('title', '')}\n"
                if ref.get('phone'): md += f"  - Phone: {ref.get('phone')}\n"
                if ref.get('email'): md += f"  - Email: {ref.get('email')}\n"
            md += "\n"

        # 3. Generate PDF from the flattened JSON
        pdf_buffer = io.BytesIO()
        create_styled_cv_from_json(flattened_json, pdf_buffer)
        pdf_buffer.seek(0)
        pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')

        return {
            "success": True,
            "original_raw_input": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text,
            "converted_json_object": converted_json,
            "flattened_json_object": flattened_json,
            "generated_markdown": md,
            "generated_pdf_base64": pdf_base64,
            "pdf_filename": f"{flattened_json.get('name', 'cv').replace(' ', '_')}_RawTest.pdf"
        }
    except Exception as e:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={
            "success": False,
            "error": str(e),
            "original_raw_input": raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
        })

@app.get("/health", summary="Health Check")
async def health_check_endpoint():
    """Check if the API and model are ready"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "tokenizer_loaded": tokenizer is not None,
        "groq_client_available": False, # Always False now that Groq is removed
        "model_path": MODEL_PATH
    }

@app.get("/", summary="API Root")
async def read_root_endpoint():
    return {"message": "Welcome to the ATS-Friendly CV Generator API! Use /docs for API documentation."} 