import { api } from './api';

// CV Data Types
export interface CVData {
  content: string;
  generatedAt: string;
  wordCount: number;
  id?: string;
  name?: string;
  savedAt?: string;
  metadata?: {
    fileName?: string;
    fileSize?: number;
    uploadDate?: string;
  };
}

export interface CVAnalysis {
  score: number;
  suggestions: string[];
  keywords: string[];
  missingKeywords: string[];
  breakdown?: {
    keywordMatch: number;
    formatting: number;
    structure: number;
    contentQuality: number;
  };
}

export interface CVOptimization {
  optimizedContent: string;
  improvements: string[];
  score: number;
  originalScore: number;
}

export interface CVDownloadOptions {
  format: 'pdf' | 'docx' | 'json' | 'txt';
  includeAnalysis?: boolean;
  template?: string;
}

// CV Generation Service
export class CVService {
  private static instance: CVService;

  private constructor() {}

  public static getInstance(): CVService {
    if (!CVService.instance) {
      CVService.instance = new CVService();
    }
    return CVService.instance;
  }

  // Generate CV with backend processing
  async generateCV(content: string, options?: { includeAnalysis?: boolean }): Promise<CVData> {
    try {
      const response = await api.post('/generate-cv-json', {
        content,
        timestamp: new Date().toISOString(),
        options
      });

      if (!response.data) {
        throw new Error('No data received from server');
      }

      return {
        content: response.data.content || content,
        generatedAt: response.data.generatedAt || new Date().toISOString(),
        wordCount: response.data.wordCount || this.calculateWordCount(content),
        metadata: response.data.metadata
      };
    } catch (error) {
      console.error('Error generating CV:', error);
      throw new Error('Failed to generate CV. Please try again.');
    }
  }

  // Analyze CV content
  async analyzeCV(content: string, jobDescription?: string): Promise<CVAnalysis> {
    try {
      const payload: any = { content };
      if (jobDescription) {
        payload.jobDescription = jobDescription;
      }

      const response = await api.post('/analyze-cv-ats', payload);
      
      if (!response.data) {
        throw new Error('No analysis data received');
      }

      return {
        score: response.data.score || 0,
        suggestions: response.data.suggestions || [],
        keywords: response.data.keywords || [],
        missingKeywords: response.data.missingKeywords || [],
        breakdown: response.data.breakdown
      };
    } catch (error) {
      console.error('Error analyzing CV:', error);
      throw new Error('Failed to analyze CV. Please try again.');
    }
  }

  // Optimize CV content
  async optimizeCV(content: string, jobDescription?: string): Promise<CVOptimization> {
    try {
      const payload: any = { content };
      if (jobDescription) {
        payload.jobDescription = jobDescription;
      }

      const response = await api.post('/optimize-cv-content', payload);
      
      if (!response.data) {
        throw new Error('No optimization data received');
      }

      return {
        optimizedContent: response.data.optimizedContent || content,
        improvements: response.data.improvements || [],
        score: response.data.score || 0,
        originalScore: response.data.originalScore || 0
      };
    } catch (error) {
      console.error('Error optimizing CV:', error);
      throw new Error('Failed to optimize CV. Please try again.');
    }
  }

  // Download CV in various formats
  async downloadCV(cvData: CVData, options: CVDownloadOptions): Promise<Blob> {
    try {
      const response = await api.post('/download-cv-pdf', {
        cvData,
        options
      }, {
        responseType: 'blob',
      });

      if (!response.data) {
        throw new Error('No file data received');
      }

      return response.data;
    } catch (error) {
      console.error('Error downloading CV:', error);
      throw new Error('Failed to download CV. Please try again.');
    }
  }

  // Save CV to local storage
  saveCVToLocal(cvData: CVData, name: string = 'cv'): void {
    try {
      const savedCVs = this.getSavedCVs();
      const cvToSave = {
        ...cvData,
        id: Date.now().toString(),
        name,
        savedAt: new Date().toISOString()
      };
      
      savedCVs.push(cvToSave);
      localStorage.setItem('savedCVs', JSON.stringify(savedCVs));
    } catch (error) {
      console.error('Error saving CV to local storage:', error);
      throw new Error('Failed to save CV locally.');
    }
  }

  // Get all saved CVs from local storage
  getSavedCVs(): CVData[] {
    try {
      const saved = localStorage.getItem('savedCVs');
      return saved ? JSON.parse(saved) : [];
    } catch (error) {
      console.error('Error reading saved CVs:', error);
      return [];
    }
  }

  // Delete saved CV
  deleteSavedCV(id: string): void {
    try {
      const savedCVs = this.getSavedCVs();
      const filteredCVs = savedCVs.filter(cv => cv.id !== id);
      localStorage.setItem('savedCVs', JSON.stringify(filteredCVs));
    } catch (error) {
      console.error('Error deleting saved CV:', error);
      throw new Error('Failed to delete saved CV.');
    }
  }

  // Calculate word count
  calculateWordCount(text: string): number {
    return text.split(/\s+/).filter(word => word.length > 0).length;
  }

  // Validate CV content
  validateCVContent(content: string): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];
    
    if (!content || content.trim().length === 0) {
      errors.push('CV content cannot be empty');
    }
    
    if (content.length < 100) {
      errors.push('CV content is too short (minimum 100 characters)');
    }
    
    if (content.length > 10000) {
      errors.push('CV content is too long (maximum 10,000 characters)');
    }
    
    const wordCount = this.calculateWordCount(content);
    if (wordCount < 50) {
      errors.push('CV content has too few words (minimum 50 words)');
    }
    
    if (wordCount > 2000) {
      errors.push('CV content has too many words (maximum 2,000 words)');
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  }

  // Extract CV metadata
  extractMetadata(content: string): {
    wordCount: number;
    characterCount: number;
    estimatedReadingTime: number;
    hasContactInfo: boolean;
    hasExperience: boolean;
    hasEducation: boolean;
    hasSkills: boolean;
  } {
    const text = content.toLowerCase();
    const wordCount = this.calculateWordCount(content);
    const characterCount = content.length;
    const estimatedReadingTime = Math.ceil(wordCount / 200); // Average reading speed
    
    return {
      wordCount,
      characterCount,
      estimatedReadingTime,
      hasContactInfo: text.includes('@') || text.includes('phone') || text.includes('email'),
      hasExperience: text.includes('experience') || text.includes('work') || text.includes('employment'),
      hasEducation: text.includes('education') || text.includes('degree') || text.includes('university'),
      hasSkills: text.includes('skills') || text.includes('competencies') || text.includes('technologies')
    };
  }

  // Format CV content for better readability
  formatCVContent(content: string): string {
    // Remove extra whitespace
    let formatted = content.replace(/\s+/g, ' ').trim();
    
    // Add line breaks for better structure
    formatted = formatted.replace(/\. /g, '.\n\n');
    formatted = formatted.replace(/:\n/g, ':\n\n');
    
    return formatted;
  }

  // Get CV templates
  getCVTemplates(): Array<{ id: string; name: string; description: string; content: string }> {
    return [
      {
        id: 'professional',
        name: 'Professional',
        description: 'Clean and professional template suitable for most industries',
        content: `[Your Name]
[Email] | [Phone] | [Location]

PROFESSIONAL SUMMARY
[Brief professional summary highlighting key skills and experience]

EXPERIENCE
[Company Name] - [Position]
[Date] - [Date]
• [Key achievement or responsibility]
• [Key achievement or responsibility]

EDUCATION
[Degree Name] - [University Name]
[Graduation Date]

SKILLS
• [Skill 1]
• [Skill 2]
• [Skill 3]`
      },
      {
        id: 'creative',
        name: 'Creative',
        description: 'Modern and creative template for design and creative roles',
        content: `[Your Name]
Creative Professional

ABOUT ME
[Personal statement about your creative approach and passion]

PORTFOLIO & PROJECTS
[Project Name] - [Role]
[Date]
[Description of the project and your contribution]

EXPERIENCE
[Company] - [Position]
[Date Range]
[Creative achievements and responsibilities]

SKILLS & TOOLS
• [Creative Skill 1]
• [Creative Skill 2]
• [Software/Tool 1]
• [Software/Tool 2]`
      },
      {
        id: 'technical',
        name: 'Technical',
        description: 'Technical template focused on programming and technical skills',
        content: `[Your Name]
Software Developer

TECHNICAL SUMMARY
[Brief summary of technical skills and experience]

TECHNICAL SKILLS
Programming Languages: [Languages]
Frameworks & Libraries: [Frameworks]
Databases: [Databases]
Tools & Technologies: [Tools]

EXPERIENCE
[Company] - [Position]
[Date Range]
• [Technical achievement with metrics]
• [Technical achievement with metrics]

PROJECTS
[Project Name]
• [Technical details and outcomes]

EDUCATION
[Degree] - [University]
[Graduation Date]`
      }
    ];
  }
}

// Export singleton instance
export const cvService = CVService.getInstance();

// Legacy functions for backward compatibility
export const generateCV = (content: string) => cvService.generateCV(content);
export const analyzeCV = (content: string, jobDescription?: string) => cvService.analyzeCV(content, jobDescription);
export const optimizeCV = (content: string, jobDescription?: string) => cvService.optimizeCV(content, jobDescription);
export const downloadCV = (cvData: CVData, format: 'pdf' | 'docx' | 'json' = 'pdf') => 
  cvService.downloadCV(cvData, { format }); 