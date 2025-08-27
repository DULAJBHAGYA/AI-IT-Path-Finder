// Free/Open ATS Scoring API Integrations

export interface ATSScoreResult {
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

// 1. ResumeWorded Free API (Limited but free)
export async function getResumeWordedScore(cvText: string): Promise<ATSScoreResult> {
  try {
    // Note: This is a mock implementation since ResumeWorded requires API key
    // In real implementation, you'd need to sign up for their free tier
    const response = await fetch('https://api.resumeworded.com/ats-score', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'Authorization': 'Bearer YOUR_API_KEY' // Get from ResumeWorded
      },
      body: JSON.stringify({
        resume: cvText,
        job_title: 'Software Developer', // Default job title
      }),
    });

    if (!response.ok) {
      throw new Error('ResumeWorded API failed');
    }

    const data = await response.json();
    return {
      score: data.score || 75,
      suggestions: data.suggestions || [],
      keywords: data.keywords || [],
      missingKeywords: data.missing_keywords || [],
    };
  } catch (error) {
    console.error('ResumeWorded API error:', error);
    throw new Error('Failed to get ATS score from ResumeWorded');
  }
}

// 2. Hugging Face Free NLP Models
export async function getHuggingFaceScore(cvText: string): Promise<ATSScoreResult> {
  try {
    // Using Hugging Face's free inference API
    const response = await fetch('https://api-inference.huggingface.co/models/facebook/bart-large-cnn', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // 'Authorization': 'Bearer YOUR_HF_TOKEN' // Get free token from Hugging Face
      },
      body: JSON.stringify({
        inputs: cvText,
        parameters: {
          max_length: 100,
          min_length: 30,
        },
      }),
    });

    if (!response.ok) {
      throw new Error('Hugging Face API failed');
    }

    const data = await response.json();
    
    // Analyze the summary for ATS compatibility
    const summary = data[0]?.summary_text || '';
    const score = calculateBasicATSScore(cvText, summary);
    
    return {
      score,
      suggestions: generateSuggestions(score),
      keywords: extractKeywords(cvText),
      missingKeywords: [],
    };
  } catch (error) {
    console.error('Hugging Face API error:', error);
    throw new Error('Failed to get ATS score from Hugging Face');
  }
}

// 3. Free Local ATS Analysis (Fallback)
export function calculateLocalATSScore(cvText: string): ATSScoreResult {
  const text = cvText.toLowerCase();
  const words = text.split(/\s+/).filter(word => word.length > 0);
  
  // Common ATS keywords
  const commonKeywords = [
    'python', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'kubernetes',
    'machine learning', 'data analysis', 'project management', 'leadership',
    'communication', 'teamwork', 'problem solving', 'analytical skills',
    'agile', 'scrum', 'git', 'api', 'rest', 'microservices'
  ];
  
  // Calculate keyword match
  const foundKeywords = commonKeywords.filter(keyword => text.includes(keyword));
  const keywordScore = (foundKeywords.length / commonKeywords.length) * 100;
  
  // Check formatting
  let formattingScore = 100;
  if (text.includes('table') || text.includes('image')) formattingScore -= 30;
  if (words.length > 2000) formattingScore -= 20;
  if (words.length < 200) formattingScore -= 15;
  
  // Check structure
  let structureScore = 100;
  if (!text.includes('email') && !text.includes('@')) structureScore -= 20;
  if (!text.includes('experience')) structureScore -= 25;
  if (!text.includes('education')) structureScore -= 20;
  if (!text.includes('skills')) structureScore -= 20;
  
  // Calculate total score
  const totalScore = Math.round(
    (keywordScore * 0.4) + (formattingScore * 0.3) + (structureScore * 0.3)
  );
  
  return {
    score: Math.max(0, Math.min(100, totalScore)),
    suggestions: generateSuggestions(totalScore),
    keywords: foundKeywords,
    missingKeywords: commonKeywords.filter(k => !foundKeywords.includes(k)).slice(0, 5),
    breakdown: {
      keywordMatch: Math.round(keywordScore),
      formatting: Math.round(formattingScore),
      structure: Math.round(structureScore),
      contentQuality: 75
    }
  };
}

// 4. Google Cloud Natural Language API (Free Tier)
export async function getGoogleNLPScore(cvText: string): Promise<ATSScoreResult> {
  try {
    // Google Cloud Natural Language API (free tier: 1000 requests/month)
    const response = await fetch(`https://language.googleapis.com/v1/documents:analyzeEntities?key=YOUR_GOOGLE_API_KEY`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        document: {
          content: cvText,
          type: 'PLAIN_TEXT',
        },
        encodingType: 'UTF8',
      }),
    });

    if (!response.ok) {
      throw new Error('Google NLP API failed');
    }

    const data = await response.json();
    const entities = data.entities || [];
    
    // Extract technical skills and keywords
    const technicalEntities = entities.filter((entity: any) => 
      entity.type === 'ORGANIZATION' || entity.type === 'OTHER'
    );
    
    const score = calculateScoreFromEntities(technicalEntities, cvText);
    
    return {
      score,
      suggestions: generateSuggestions(score),
      keywords: technicalEntities.map((e: any) => e.name).slice(0, 10),
      missingKeywords: [],
    };
  } catch (error) {
    console.error('Google NLP API error:', error);
    throw new Error('Failed to get ATS score from Google NLP');
  }
}

// Helper functions
function calculateBasicATSScore(cvText: string, summary: string): number {
  const text = cvText.toLowerCase();
  const summaryLower = summary.toLowerCase();
  
  // Simple scoring based on content analysis
  let score = 70; // Base score
  
  // Bonus for having a summary
  if (summaryLower.length > 50) score += 10;
  
  // Bonus for technical keywords
  const techKeywords = ['python', 'javascript', 'react', 'sql', 'aws'];
  const foundTech = techKeywords.filter(k => text.includes(k));
  score += (foundTech.length / techKeywords.length) * 15;
  
  // Bonus for action verbs
  const actionVerbs = ['developed', 'implemented', 'managed', 'created'];
  const foundVerbs = actionVerbs.filter(v => text.includes(v));
  score += (foundVerbs.length / actionVerbs.length) * 5;
  
  return Math.min(100, score);
}

function generateSuggestions(score: number): string[] {
  const suggestions = [];
  
  if (score < 60) {
    suggestions.push('Add more relevant keywords from the job description');
    suggestions.push('Include quantifiable achievements and metrics');
    suggestions.push('Use action verbs to describe your experience');
  } else if (score < 80) {
    suggestions.push('Consider adding more industry-specific terminology');
    suggestions.push('Ensure all required sections are present');
    suggestions.push('Remove any complex formatting or tables');
  } else {
    suggestions.push('Great job! Your CV is well-optimized for ATS');
    suggestions.push('Consider customizing keywords for specific job applications');
  }
  
  return suggestions;
}

function extractKeywords(text: string): string[] {
  const commonKeywords = [
    'python', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
    'project management', 'leadership', 'communication', 'teamwork'
  ];
  
  return commonKeywords.filter(keyword => 
    text.toLowerCase().includes(keyword.toLowerCase())
  );
}

function calculateScoreFromEntities(entities: any[], cvText: string): number {
  let score = 70;
  
  // Score based on number of relevant entities found
  const relevantEntities = entities.filter(e => e.salience > 0.01);
  score += Math.min(20, relevantEntities.length * 2);
  
  // Score based on entity types
  const hasTechnicalTerms = entities.some(e => 
    e.type === 'ORGANIZATION' || e.type === 'OTHER'
  );
  if (hasTechnicalTerms) score += 10;
  
  return Math.min(100, score);
}

// Main function to get ATS score (tries multiple APIs)
export async function getATSScore(cvText: string, apiPreference: 'resumeworded' | 'huggingface' | 'google' | 'local' = 'local'): Promise<ATSScoreResult> {
  try {
    switch (apiPreference) {
      case 'resumeworded':
        return await getResumeWordedScore(cvText);
      case 'huggingface':
        return await getHuggingFaceScore(cvText);
      case 'google':
        return await getGoogleNLPScore(cvText);
      case 'local':
      default:
        return calculateLocalATSScore(cvText);
    }
  } catch (error) {
    console.error('API failed, falling back to local analysis:', error);
    return calculateLocalATSScore(cvText);
  }
} 