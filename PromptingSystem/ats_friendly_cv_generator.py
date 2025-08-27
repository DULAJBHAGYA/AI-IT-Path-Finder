#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ATS-Friendly CV Generator
A standalone Python script to generate professional CVs from text input.
"""

import os
import sys
import json
import re
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch
from textblob import TextBlob
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Configure the Groq API key
try:
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    print("✅ Groq client initialized successfully.")
except Exception as e:
    print(f"❌ Failed to initialize Groq client: {e}")
    client = None

def generate_structured_json(cv_text):
    if not client:
        print("❌ Groq client not initialized. Cannot proceed.")
        return None
        
    print("🤖 Step 1: Calling Groq (Llama 3) to extract JSON from text...")
    prompt_to_json = f"""
    You are an expert resume parser. Extract all information from the CV text below into a structured JSON format.
    Follow this JSON schema precisely:
    {{
      "name": "string",
      "job_title": "string",
      "contact": {{
        "email": "string",
        "phone": "string",
        "linkedin": "string",
        "github": "string",
        "website": "string",
        "location": "string"
      }},
      "profile_summary": "string",
      "skills": [
        {{
          "category": "string",
          "items": ["string"]
        }}
      ],
      "experience": [
        {{
          "title": "string",
          "company": "string",
          "duration": "string",
          "responsibilities": ["string"]
        }}
      ],
      "projects": [
        {{
          "name": "string",
          "role": "string",
          "description": "string",
          "technologies": ["string"]
        }}
      ],
      "education": [
        {{
          "degree": "string",
          "institution": "string",
          "duration": "string",
          "details": "string"
        }}
      ],
      "volunteering_and_leadership": ["string"],
      "references": [
        {{
          "name": "string",
          "title": "string",
          "phone": "string",
          "email": "string"
        }}
      ]
    }}
    Respond with ONLY the JSON object, without any surrounding text or markdown.

    CV Text to Parse:
    ---
    {cv_text}
    ---
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_to_json,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        json_output = chat_completion.choices[0].message.content
        cv_json = json.loads(json_output)
        print("✅ Successfully generated and parsed JSON from Groq response.")
        return cv_json
    except Exception as e:
        print(f"❌ An error occurred during JSON extraction: {e}")
        return None

def generate_markdown_cv(cv_json):
    if not client:
        print("❌ Groq client not initialized. Cannot proceed.")
        return ""
        
    print("🤖 Step 2: Generating Markdown from JSON using Groq...")
    if not cv_json:
        return ""
    
    prompt_to_cv = f"""
    You are a professional resume writer. Generate a simple, clean, and ATS-friendly resume in Markdown format using the provided JSON data.
    - Use '#' for the candidate's name.
    - Use '##' for main section headings (e.g., SUMMARY, SKILLS, EXPERIENCE).
    - Use '*' for bullet points.
    
    JSON Data:
    ```json
    {json.dumps(cv_json, indent=2)}
    ```
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_to_cv,
                }
            ],
            model="llama3-8b-8192",
            temperature=0.7,
        )
        cv_markdown = chat_completion.choices[0].message.content
        print("✅ Successfully generated formatted CV from JSON.")
        return cv_markdown
    except Exception as e:
        print(f"❌ An error occurred during Markdown generation: {e}")
        return ""

def add_word_spacing(text):
    # Add a space after every comma if not present
    text = re.sub(r',(?=[^\s])', ', ', text)
    # Add space between lowercase and uppercase letters (e.g., 'anddedicated' -> 'and dedicated')
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Add space between words that are run together (e.g., 'qualities,whoiswilling' -> 'qualities, who is willing')
    text = re.sub(r'([a-zA-Z])([A-Z][a-z])', r'\1 \2', text)
    # Add space between lowercase and next word if missing (e.g., 'anddedicated' -> 'and dedicated')
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Remove double spaces
    text = re.sub(r'\s{2,}', ' ', text)
    return text

def draw_justified_paragraph(c, text, x, y, width, font_name, font_size, line_height, indent=12, extra_word_space=2):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    import re
    # Split into paragraphs by double newlines or periods followed by space
    paragraphs = re.split(r'\n\s*|(?<=\.)\s{2,}', text)
    for para in paragraphs:
        words = para.split()
        if not words:
            y -= line_height
            continue
        lines = []
        current_line = []
        current_width = 0
        for word in words:
            word_width = stringWidth(word + ' ', font_name, font_size)
            if current_width + word_width + extra_word_space <= width:
                current_line.append(word)
                current_width += word_width + extra_word_space
            else:
                lines.append(current_line)
                current_line = [word]
                current_width = word_width + extra_word_space
        if current_line:
            lines.append(current_line)
        for i, line_words in enumerate(lines):
            if i == 0:
                x_start = x + indent  # Indent first line
            else:
                x_start = x
            if i == len(lines) - 1 or len(line_words) == 1:
                # Add extra space between words
                x_pos = x_start
                for word in line_words:
                    c.drawString(x_pos, y, word)
                    word_width = stringWidth(word, font_name, font_size)
                    x_pos += word_width + extra_word_space
            else:
                total_words = len(line_words)
                line_text = ' '.join(line_words)
                line_width = stringWidth(line_text, font_name, font_size)
                space_count = total_words - 1
                if space_count > 0:
                    extra_space = (width - line_width) / space_count + extra_word_space
                else:
                    extra_space = extra_word_space
                x_pos = x_start
                for j, word in enumerate(line_words):
                    c.drawString(x_pos, y, word)
                    word_width = stringWidth(word, font_name, font_size)
                    x_pos += word_width
                    if j < space_count:
                        x_pos += extra_space
            y -= line_height
        y -= 2  # Extra space between paragraphs
    return y

def create_styled_cv_from_json(data, file_name="generated_cv.pdf"):
    """Generate an ATS-compatible PDF CV that fits within 2 A4 pages, with grammar/spelling correction and quantification checks."""
    c = canvas.Canvas(file_name, pagesize=A4)
    width, height = A4

    # Define margins and layout (standard margins for ATS compatibility)
    left_margin = 0.5 * inch
    right_margin = width - 0.5 * inch
    top_margin = height - 0.5 * inch
    bottom_margin = 0.5 * inch
    content_width = width - 1 * inch

    # Starting position
    y_pos = top_margin
    x_pos = left_margin
    page_count = 1

    # --- Start of Header/Contact Info Drawing ---
    
    # Get contact info directly from the data object
    name = data.get('name', 'Your Name')
    job_title = data.get('job_title', 'Job Title')
    contact_info = data.get('contact', {})
    
    email = contact_info.get('email', '')
    phone = contact_info.get('phone', '')
    location = contact_info.get('location', '')
    linkedin = contact_info.get('linkedin', '')
    github = contact_info.get('github', '')
    website = contact_info.get('website', '')

    # Set fonts and draw the text
    c.setFont('Helvetica-Bold', 18)
    c.drawCentredString(width / 2.0, y_pos, name)
    y_pos -= 18

    if job_title:
        c.setFont('Helvetica', 12)
        c.drawCentredString(width / 2.0, y_pos, job_title)
        y_pos -= 15

    # Assemble contact line, filtering out empty values
    contact_parts = [part for part in [email, phone, location, linkedin, github, website] if part]
    contact_line = " | ".join(contact_parts)
    
    if contact_line:
        c.setFont('Helvetica', 10)
        c.drawCentredString(width / 2.0, y_pos, contact_line)
        y_pos -= 15

    # --- Horizontal Line ---
    max_text_width = max(
        c.stringWidth(name, 'Helvetica-Bold', 18),
        c.stringWidth(job_title, 'Helvetica', 12),
        c.stringWidth(contact_line, 'Helvetica', 10)
    )
    line_margin = 20 
    line_x_start = (width - max_text_width) / 2 - line_margin
    line_x_end = (width + max_text_width) / 2 + line_margin
    line_y = y_pos + 5 # Adjust position to be after contact info
    c.setLineWidth(0.5)
    c.line(line_x_start, line_y, line_x_end, line_y)
    y_pos = line_y - 15

    # SUMMARY Section - justified, no indent, proper word spacing
    summary_text = data.get('profile_summary', '')
    c.setFont('Helvetica', 10)
    summary_text_corrected = str(TextBlob(summary_text).correct())
    summary_text_corrected = add_word_spacing(summary_text_corrected)
    y_pos = draw_justified_paragraph(c, summary_text_corrected, x_pos, y_pos, content_width, 'Helvetica', 10, 12, indent=0)
    y_pos -= 5

    # Check if we need a new page
    if y_pos < 150:  # Reduced threshold
        c.showPage()
        y_pos = top_margin
        page_count += 1
        if page_count > 2:  # Limit to 2 pages
            c.save()
            print(f"📄 Successfully created compact CV at '{file_name}' (2 pages max)")
            return file_name

    # SKILLS Section - ATS-friendly standard title
    c.setFont('Helvetica-Bold', 12)  # Standard size
    c.drawString(x_pos, y_pos, 'SKILLS')
    y_pos -= 20

    skills = data.get('skills', [])
    for skill_cat in skills:
        # Category name - ATS-friendly
        c.setFont('Helvetica-Bold', 11)  # Standard size
        c.drawString(x_pos, y_pos, skill_cat.get('category', ''))
        y_pos -= 15

        # Skills in category - ATS-friendly format with commas
        c.setFont('Helvetica', 10)  # Standard size
        skills_list = skill_cat.get('items', [])
        skills_text = ", ".join(skills_list)  # Use commas instead of bullets for ATS

        # Wrap skills if they exceed page width
        words = skills_text.split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if c.stringWidth(test_line, 'Helvetica', 10) <= content_width:
                current_line = test_line
            else:
                if current_line:
                    c.drawString(x_pos, y_pos, current_line.strip())
                    y_pos -= 12
                current_line = word + " "
        if current_line:
            c.drawString(x_pos, y_pos, current_line.strip())
        y_pos -= 15

    y_pos -= 10

    # Check if we need a new page
    if y_pos < 200:  # Reduced threshold
        c.showPage()
        y_pos = top_margin
        page_count += 1
        if page_count > 2:  # Limit to 2 pages
            c.save()
            print(f"📄 Successfully created compact CV at '{file_name}' (2 pages max)")
            return file_name

    # WORK EXPERIENCE Section - ATS-friendly with quantification suggestion
    experience = data.get('experience', [])
    if experience:
        c.setFont('Helvetica-Bold', 12)  # Standard size
        c.drawString(x_pos, y_pos, 'WORK EXPERIENCE')
        y_pos -= 20
        for job in experience:
            # Job title and company - ATS-friendly format
            c.setFont('Helvetica-Bold', 11)  # Standard size
            title_line = f"{job.get('title', '')}, {job.get('company', '')}"
            c.drawString(x_pos, y_pos, title_line)
            y_pos -= 15
            # Duration
            c.setFont('Helvetica', 10)  # Standard size
            c.drawString(x_pos, y_pos, job.get('duration', ''))
            y_pos -= 15
            # Responsibilities - ATS-friendly with action verbs
            c.setFont('Helvetica', 10)  # Standard size
            responsibilities = job.get('responsibilities', [])
            for resp in responsibilities:
                resp_text = resp.strip()
                resp_text = str(TextBlob(resp_text).correct())
                # Remove all statements inside brackets (parentheses)
                resp_text = re.sub(r'\s*\(.*?\)', '', resp_text).strip()
                if len(resp_text) > 150:
                    resp_text = resp_text[:147] + "..."
                c.drawString(x_pos, y_pos, "• " + resp_text)
                y_pos -= 12
                if y_pos < 100:
                    c.showPage()
                    y_pos = top_margin
                    page_count += 1
                    if page_count > 2:
                        c.save()
                        print(f"📄 Successfully created ATS-compatible CV at '{file_name}' (2 pages max)")
                        return file_name
            y_pos -= 15

    # PROJECTS Section - justified with extra word spacing, no indent (all lines start at same left margin)
    projects = data.get('projects', [])
    if projects and page_count <= 2:
        # Check if we need a new page
        if y_pos < 150:  # Standard threshold
            c.showPage()
            y_pos = top_margin
            page_count += 1
            if page_count > 2:  # Limit to 2 pages
                c.save()
                print(f"📄 Successfully created ATS-compatible CV at '{file_name}' (2 pages max)")
                return file_name

        c.setFont('Helvetica-Bold', 12)  # Standard size
        c.drawString(x_pos, y_pos, 'PROJECTS')
        y_pos -= 20

        # Include all projects but with ATS-friendly formatting
        for proj in projects:
            # Project name and role - ATS-friendly format
            c.setFont('Helvetica-Bold', 10)  # Standard size
            project_title = proj.get('name', '')
            if proj.get('role'):
                project_title += f" - {proj.get('role', '')}"
            c.drawString(x_pos, y_pos, project_title)
            y_pos -= 12
            c.setFont('Helvetica', 10)
            desc = proj.get('description', '')
            desc = str(TextBlob(desc).correct())
            desc = add_word_spacing(desc)
            desc = desc.replace('\n', ' ').strip()
            # Do NOT add any quantifiable example statements here
            y_pos = draw_justified_paragraph(c, desc, x_pos, y_pos, content_width, 'Helvetica', 10, 12, indent=0, extra_word_space=2)

            # Technologies - ATS-friendly format
            if proj.get('technologies'):
                tech_line = "Technologies: " + ", ".join(proj.get('technologies', []))
                c.setFont('Helvetica', 9)  # Slightly smaller for tech list
                # Wrap technologies if too long
                if c.stringWidth(tech_line, 'Helvetica', 9) > content_width:
                    tech_words = tech_line.split()
                    current_line = ""
                    for word in tech_words:
                        test_line = current_line + word + " "
                        if c.stringWidth(test_line, 'Helvetica', 9) <= content_width:
                            current_line = test_line
                        else:
                            if current_line:
                                c.drawString(x_pos, y_pos, current_line.strip())
                                y_pos -= 10
                            current_line = word + " "
                    if current_line:
                        c.drawString(x_pos, y_pos, current_line.strip())
                        y_pos -= 10
                else:
                    c.drawString(x_pos, y_pos, tech_line)
                    y_pos -= 10

            y_pos -= 15

            # Check if we need a new page
            if y_pos < 120:  # Standard threshold
                c.showPage()
                y_pos = top_margin
                page_count += 1
                if page_count > 2:  # Limit to 2 pages
                    c.save()
                    print(f"📄 Successfully created ATS-compatible CV at '{file_name}' (2 pages max)")
                    return file_name

    # EDUCATION Section - compact
    c.setFont('Helvetica-Bold', 12)
    c.drawString(x_pos, y_pos, 'EDUCATION')
    y_pos -= 15
    education = data.get('education', [])
    for edu in education:
        c.setFont('Helvetica-Bold', 10)
        degree = edu.get('degree', '')
        c.drawString(x_pos, y_pos, degree)
        y_pos -= 10
        c.drawString(x_pos, y_pos, edu.get('institution', ''))
        y_pos -= 10
        c.setFont('Helvetica', 10)
        if edu.get('details'):
            c.drawString(x_pos, y_pos, edu.get('details', ''))
            y_pos -= 10
        if edu.get('duration'):
            c.drawString(x_pos, y_pos, edu.get('duration', ''))
            y_pos -= 10
        y_pos -= 10

    # VOLUNTEERING & LEADERSHIP - compact
    volunteering = data.get('volunteering_and_leadership', [])
    if volunteering and page_count <= 2:
        # Check if we need a new page
        if y_pos < 100:  # Reduced threshold
            c.showPage()
            y_pos = top_margin
            page_count += 1
            if page_count > 2:  # Limit to 2 pages
                # Instead of 'break', just return to exit the function early
                c.save()
                print(f"📄 Successfully created compact CV at '{file_name}' (2 pages max)")
                return file_name

        c.setFont('Helvetica-Bold', 12)
        c.drawString(x_pos, y_pos, 'VOLUNTEERING & LEADERSHIP')
        y_pos -= 15

        c.setFont('Helvetica', 10)  # Reduced from 10
        # Limit to 5 most important
        for vol in volunteering[:5]:
            vol_text = vol
            if len(vol_text) > 100:
                vol_text = vol_text[:97] + "..."
            c.drawString(x_pos, y_pos, "• " + vol_text)
            y_pos -= 12  # Reduced from 13
        y_pos -= 10  # Reduced from 15

    # REFERENCES - only if space allows
    references = data.get('references', [])
    if references and page_count <= 2 and y_pos > 150:
        c.setFont('Helvetica-Bold', 12)
        c.drawString(x_pos, y_pos, 'REFERENCES')
        y_pos -= 15

        # Only include first 2 references
        for ref in references[:2]:
            c.setFont('Helvetica-Bold', 10)
            c.drawString(x_pos, y_pos, ref.get('name', ''))
            y_pos -= 10

            c.setFont('Helvetica', 10)
            c.drawString(x_pos, y_pos, ref.get('title', ''))
            y_pos -= 10
            c.drawString(x_pos, y_pos, ref.get('phone', ''))
            y_pos -= 10
            c.drawString(x_pos, y_pos, ref.get('email', ''))
            y_pos -= 15

    c.save()
    print(f"📄 Successfully created ATS-compatible CV at '{file_name}' (2 pages max)")
    return file_name

def main():
    """Main function to run the CV generator."""
    print("🚀 ATS-Friendly CV Generator")
    print("="*50)
    
    # Get CV text from terminal input
    print("📝 Please paste the full text of your CV below. Press Ctrl-D (or Ctrl-Z on Windows) when you are finished.")
    cv_text_input = sys.stdin.read()

    if not cv_text_input.strip():
        print("No input received. Exiting.")
        return

    # 1. Generate Structured JSON from CV text
    cv_data = generate_structured_json(cv_text_input)

    if cv_data:
        # Display the intermediate JSON
        print("\n--- ✨ Extracted CV Data (JSON Format) ✨ ---\n")
        print(json.dumps(cv_data, indent=2))
        
        # Generate Markdown CV
        cv_markdown = generate_markdown_cv(cv_data)
        
        if cv_markdown:
            # Display the intermediate Markdown CV
            print("\n--- ✨ Generated CV (Markdown Format) ✨ ---\n")
            print(cv_markdown)
            
            # Generate PDF
            print("\n🚀 Step 3: Starting final PDF generation...")
            try:
                # Get filename from user
                default_filename = f"{cv_data.get('personal_info', {}).get('name', 'cv').replace(' ', '_')}_CV.pdf"
                filename = input(f"Enter PDF filename (default: {default_filename}): ").strip()
                if not filename:
                    filename = default_filename
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
                
                pdf_file_name = create_styled_cv_from_json(cv_data, filename)
                print(f"✅ PDF '{pdf_file_name}' generated successfully!")
                print(f"📁 File saved at: {os.path.abspath(pdf_file_name)}")
                
            except Exception as e:
                print(f"❌ An error occurred during PDF generation: {e}")
        else:
            print("❌ Could not generate Markdown CV.")
    else:
        print("❌ Could not extract structured data from CV text.")

if __name__ == "__main__":
    main()