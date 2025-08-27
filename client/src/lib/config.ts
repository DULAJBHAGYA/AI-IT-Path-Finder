// Configuration for the application
export const config = {
  BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://f4b626e1610f.ngrok-free.app',
  
  ENDPOINTS: {
    GENERATE_CV_JSON: '/generate-cv-json',
    DOWNLOAD_CV_PDF: '/download-cv-pdf',
    PREVIEW_CV_JSON: '/preview-cv-json'
  },
  
  DEFAULT_CV_TEMPLATE: `Enter your CV content here...

PERSONAL INFORMATION:
Name: [Your Full Name]
Email: [your.email@example.com]
Phone: [Your Phone Number]
Location: [City, Country]

PROFESSIONAL SUMMARY:
[Write a compelling 2-3 sentence summary of your professional background, key skills, and career objectives]

WORK EXPERIENCE:
[Company Name] - [Job Title]
[Start Date] - [End Date]
• [Key achievement or responsibility]
• [Key achievement or responsibility]
• [Key achievement or responsibility]

EDUCATION:
[Degree Name] - [University/Institution]
[Graduation Year]
[Relevant coursework or achievements]

SKILLS:
Technical Skills: [Skill 1, Skill 2, Skill 3]
Soft Skills: [Skill 1, Skill 2, Skill 3]
Languages: [Language 1, Language 2]

CERTIFICATIONS:
[Certification Name] - [Issuing Organization] - [Year]

PROJECTS:
[Project Name]
• [Description and technologies used]
• [Outcomes and achievements]`
}; 