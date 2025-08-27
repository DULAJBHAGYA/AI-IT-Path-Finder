from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import io
import re
import sys
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from tqdm import tqdm

MODEL_DIR = "./final_merged_model_v2"
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)

# Load model with optimizations
print("🔄 Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    torch_dtype=torch.float16,  # Use half precision for faster inference
    low_cpu_mem_usage=True,     # Reduce memory usage
    device_map=None             # Load on CPU first, then move to best device
)
model.eval()

# Try to use GPU if available
if torch.cuda.is_available():
    print("🚀 GPU detected! Moving model to GPU for faster inference...")
    model = model.cuda()
elif torch.backends.mps.is_available():
    print("🚀 MPS (Apple Silicon) detected! Using MPS for faster inference...")
    try:
        model = model.to("mps")
        # Test MPS compatibility
        test_input = torch.randn(1, 10).to("mps")
        _ = model(test_input)
        print("✅ MPS device working correctly!")
    except Exception as e:
        print(f"⚠️  MPS device failed: {e}")
        print("🔄 Falling back to CPU...")
        model = model.cpu()
        try:
            model = torch.compile(model, mode="reduce-overhead")
            print("✅ CPU optimization applied!")
        except Exception as e2:
            print(f"⚠️  CPU optimization failed: {e2}")
            print("   Continuing with standard CPU inference...")
else:
    print("⚠️  No GPU detected. Using CPU (will be slower).")
    # Optimize for CPU
    try:
        model = torch.compile(model, mode="reduce-overhead")
        print("✅ CPU optimization applied!")
    except Exception as e:
        print(f"⚠️  CPU optimization failed: {e}")
        print("   Continuing with standard CPU inference...")

app = FastAPI(
    title="ATS-Friendly CV Generator API",
    description="API to generate structured CV data, Markdown, and PDF from unstructured text using a fine-tuned LLM.",
    version="2.2.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def build_prompt(cv_text):
    return (
        "<|system|>You are an expert resume parser that extracts information from CV text and returns it as JSON.</s>\n"
        f"<|user|>{cv_text}</s>\n"
        "<|assistant|>"
    )

def flatten_cv_json(cv_json):
    if 'experience' in cv_json and isinstance(cv_json['experience'], list) and len(cv_json['experience']) > 0:
        exp0 = cv_json['experience'][0]
        for key in ['projects', 'education', 'volunteering_and_leadership', 'references']:
            if key in exp0 and key not in cv_json:
                cv_json[key] = exp0[key]
    for key in ['job_title', 'skills', 'projects', 'education', 'volunteering_and_leadership', 'references']:
        if key not in cv_json:
            cv_json[key] = [] if key != 'job_title' else ""
    return cv_json

def extract_json_from_text(text):
    # Try to extract the first JSON object from the text
    match = re.search(r'({.*?})', text, re.DOTALL)
    if match:
        return match.group(1)
    return text

def generate_structured_json(cv_text, max_new_tokens=1024):
    print("\n" + "="*60)
    print("🚀 STARTING CV GENERATION PROCESS")
    print("="*60)
    
    print("\n🔄 Building prompt...")
    prompt = build_prompt(cv_text)
    
    print("🔄 Tokenizing input...")
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    
    # Move inputs to the same device as model
    device = next(model.parameters()).device
    input_ids = input_ids.to(device)
    attention_mask = attention_mask.to(device)
    
    print("\n🔄 Generating response with model...")
    print("   Optimizing for speed...")
    
    with torch.no_grad():
        # Create progress bar for generation with better terminal formatting
        with tqdm(
            total=max_new_tokens, 
            desc="🤖 Generating tokens", 
            unit="tokens",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
            file=sys.stdout,
            dynamic_ncols=True
        ) as pbar:
            
            # Use streaming generation for real-time progress
            generated_tokens = 0
            current_input_ids = input_ids.clone()
            
            for _ in range(max_new_tokens):
                # Generate next token
                outputs = model(current_input_ids, attention_mask=attention_mask, use_cache=True)
                next_token_logits = outputs.logits[:, -1, :]
                next_token = torch.argmax(next_token_logits, dim=-1).unsqueeze(0)
                
                # Append to input (ensure device consistency)
                current_input_ids = torch.cat([current_input_ids, next_token], dim=-1)
                attention_mask = torch.cat([attention_mask, torch.ones(1, 1, device=device)], dim=-1)
                
                generated_tokens += 1
                pbar.update(1)
                
                # Check for EOS token
                if next_token.item() == tokenizer.eos_token_id:
                    break
            
            output = current_input_ids
    
    print("\n🔄 Decoding response...")
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    
    print("\n" + "="*40)
    print("📄 RAW MODEL OUTPUT")
    print("="*40)
    print(response)
    print("="*40)
    
    print("\n🔄 Extracting JSON from response...")
    # Extract only the assistant's response
    if "<|assistant|>" in response:
        response = response.split("<|assistant|>")[-1].strip()
    json_str = extract_json_from_text(response)
    
    print("Step 6: Parsing and validating the final JSON structure...")
    try:
        cv_json = json.loads(json_str)
        # -- MODIFICATION: The `flatten_cv_json` step has been removed as requested. --
        # This function was responsible for the final "ATS-friendly" structuring.
        # cv_json = flatten_cv_json(cv_json) # This line has been removed.

        print("\n" + "✅" * 30)
        print("✅ SECTION IDENTIFICATION AND JSON CREATION COMPLETE!")
        print("⚠️  NOTE: The final 'ATS-friendly' structuring step has been removed as requested.")
        print("✅" * 30)
        
        # -- MODIFICATION: The following log messages that looked like a score
        # -- have been removed as requested.
        # print(f"✅ Extracted CV for: {cv_json.get('name', 'Unknown')}")
        # print(f"✅ Job Title: {cv_json.get('job_title', 'Not specified')}")
        # experience = cv_json.get('experience', [])
        # education = cv_json.get('education', [])
        # skills = cv_json.get('skills', [])
        # print(f"✅ Experience entries: {len(experience)}")
        # print(f"✅ Education entries: {len(education)}")
        # print(f"✅ Skills categories: {len(skills)}")

    except Exception as e:
        print("\n" + "❌" + "="*58)
        print("❌ JSON PARSE ERROR")
        print("❌" + "="*58)
        print(f"❌ Error: {e}")
        raise ValueError("Model output is not valid JSON") from e
    
    return cv_json

def generate_markdown_cv(cv_json):
    md = f"# {cv_json.get('name', '')}\n"
    md += f"**{cv_json.get('job_title', '')}**\n\n"
    md += f"## Contact\n"
    for k, v in cv_json.get('contact', {}).items():
        if v:
            md += f"- {k.title()}: {v}\n"
    md += f"\n## Summary\n{cv_json.get('profile_summary', '')}\n"
    # Add skills
    skills = cv_json.get('skills', [])
    if skills:
        md += "\n## Skills\n"
        for skill_cat in skills:
            cat = skill_cat.get('category', '')
            items = ', '.join(skill_cat.get('items', []))
            md += f"- {cat}: {items}\n"
    # Add experience
    experience = cv_json.get('experience', [])
    if experience:
        md += "\n## Work Experience\n"
        for exp in experience:
            md += f"- {exp.get('title', '')}, {exp.get('company', '')} ({exp.get('duration', '')})\n"
            for resp in exp.get('responsibilities', []):
                md += f"  - {resp}\n"
    # Add education
    education = cv_json.get('education', [])
    if education:
        md += "\n## Education\n"
        for edu in education:
            md += f"- {edu.get('degree', '')}, {edu.get('institution', '')} ({edu.get('duration', '')})\n"
            if edu.get('details', ''):
                md += f"  - {edu.get('details', '')}\n"
    return md

def generate_pdf_cv(cv_json):
    print("\n" + "="*50)
    print("📄 STARTING PDF GENERATION")
    print("="*50)
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40

    # Calculate total sections for progress bar
    total_sections = 4  # Basic info, skills, experience, education
    if cv_json.get('skills'):
        total_sections += len(cv_json.get('skills', []))
    if cv_json.get('experience'):
        total_sections += len(cv_json.get('experience', []))
    if cv_json.get('education'):
        total_sections += len(cv_json.get('education', []))

    print(f"\n📊 Total sections to process: {total_sections}")
    print("🔄 Creating PDF sections...")

    with tqdm(
        total=total_sections, 
        desc="📄 Generating PDF sections", 
        unit="section",
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
        file=sys.stdout,
        dynamic_ncols=True
    ) as pbar:
        # Basic info
        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, cv_json.get('name', ''))
        y -= 24
        c.setFont("Helvetica", 12)
        c.drawString(40, y, cv_json.get('job_title', ''))
        y -= 24
        pbar.update(1)

        # Contact
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Contact")
        y -= 18
        c.setFont("Helvetica", 10)
        for k, v in cv_json.get('contact', {}).items():
            if v:
                c.drawString(50, y, f"{k.title()}: {v}")
                y -= 14
        pbar.update(1)

        # Summary
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Summary")
        y -= 18
        c.setFont("Helvetica", 10)
        summary = cv_json.get('profile_summary', '')
        for line in summary.split('\n'):
            c.drawString(50, y, line[:100])
            y -= 14
        y -= 10
        pbar.update(1)

        # Skills
        skills = cv_json.get('skills', [])
        if skills:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Skills")
            y -= 18
            c.setFont("Helvetica", 10)
            for skill_cat in skills:
                cat = skill_cat.get('category', '')
                items = ', '.join(skill_cat.get('items', []))
                c.drawString(50, y, f"{cat}: {items}")
                y -= 14
                pbar.update(1)
            y -= 10

        # Experience
        experience = cv_json.get('experience', [])
        if experience:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Work Experience")
            y -= 18
            c.setFont("Helvetica", 10)
            for exp in experience:
                c.drawString(50, y, f"{exp.get('title', '')}, {exp.get('company', '')} ({exp.get('duration', '')})")
                y -= 14
                for resp in exp.get('responsibilities', []):
                    c.drawString(60, y, f"- {resp}")
                    y -= 12
                y -= 6
                pbar.update(1)
            y -= 10

        # Education
        education = cv_json.get('education', [])
        if education:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Education")
            y -= 18
            c.setFont("Helvetica", 10)
            for edu in education:
                c.drawString(50, y, f"{edu.get('degree', '')}, {edu.get('institution', '')} ({edu.get('duration', '')})")
                y -= 14
                if edu.get('details', ''):
                    c.drawString(60, y, f"- {edu.get('details', '')}")
                    y -= 12
                pbar.update(1)
            y -= 10

    print("\n🔄 Saving PDF to buffer...")
    c.save()
    buffer.seek(0)
    
    print("\n" + "✅" + "="*48)
    print("✅ PDF GENERATION COMPLETED SUCCESSFULLY!")
    print("✅" + "="*48)
    print(f"✅ PDF size: {len(buffer.getvalue())} bytes")
    print(f"✅ Filename: {cv_json.get('name', 'cv').replace(' ', '_')}_CV.pdf")
    
    return buffer

@app.post("/generate-cv-json")
def generate_cv_json(cv_text: str = Form(...)):
    if not cv_text.strip():
        return JSONResponse(status_code=400, content={"error": "CV text cannot be empty."})
    try:
        cv_json = generate_structured_json(cv_text)
        return {"json": cv_json}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-cv-markdown")
def generate_cv_markdown(cv_text: str = Form(...)):
    if not cv_text.strip():
        return JSONResponse(status_code=400, content={"error": "CV text cannot be empty."})
    try:
        cv_json = generate_structured_json(cv_text)
        markdown_cv = generate_markdown_cv(cv_json)
        return {"markdown": markdown_cv}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate-cv-pdf")
def generate_cv_pdf(cv_text: str = Form(...)):
    if not cv_text.strip():
        return JSONResponse(status_code=400, content={"error": "CV text cannot be empty."})
    try:
        cv_json = generate_structured_json(cv_text)
        pdf_buffer = generate_pdf_cv(cv_json)
        filename = f"{cv_json.get('name', 'cv').replace(' ', '_')}_CV.pdf"
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/")
def read_root():
    return {"message": "Welcome to the ATS-Friendly CV Generator API! Use /generate-cv-json, /generate-cv-markdown, or /generate-cv-pdf."} 