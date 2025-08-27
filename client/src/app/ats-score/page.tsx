'use client';

import { useState } from 'react';
import { Upload, Target, Moon, Sun, ArrowLeft, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { useTheme } from '@/contexts/ThemeContext';
import { getATSScore, ATSScoreResult } from '@/lib/atsApi';

export default function ATSScorePage() {
  const { isDarkMode, toggleTheme } = useTheme();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [atsScore, setAtsScore] = useState<number | null>(null);
  const [atsResult, setAtsResult] = useState<ATSScoreResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [fileName, setFileName] = useState('');
  const [cvText, setCvText] = useState('');

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      setUploadedFile(file);
      setFileName(file.name);
      setAtsScore(null);
      setAtsResult(null);
      
      // Extract text from PDF (simplified - in real app, you'd use a PDF parser)
      const reader = new FileReader();
      reader.onload = (e) => {
        const text = e.target?.result as string;
        setCvText(text);
      };
      reader.readAsText(file);
    } else {
      alert('Please upload a PDF file');
    }
  };

  const handleAnalyze = async () => {
    if (!uploadedFile || !cvText) {
      alert('Please upload a PDF file first');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      // Use real ATS scoring API
      const result = await getATSScore(cvText, 'local'); // Default to local analysis
      setAtsResult(result);
      setAtsScore(result.score);
    } catch (error) {
      console.error('ATS analysis failed:', error);
      alert('Failed to analyze CV. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-500';
    if (score >= 60) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getScoreMessage = (score: number) => {
    if (score >= 80) return 'Excellent! Your CV is highly ATS-friendly.';
    if (score >= 60) return 'Good! Your CV has decent ATS compatibility.';
    return 'Needs improvement. Consider optimizing your CV for better ATS scores.';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="w-8 h-8 text-green-500" />;
    if (score >= 60) return <AlertCircle className="w-8 h-8 text-yellow-500" />;
    return <AlertCircle className="w-8 h-8 text-red-500" />;
  };

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDarkMode ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900' : 'bg-gradient-to-br from-blue-50 via-white to-blue-100'}`}>
      <div className="container mx-auto px-4 py-4 max-w-4xl">
        {/* Header with Back Button and Theme Toggle */}
        <div className="flex items-center justify-between mb-8">
          <Link 
            href="/cv-form"
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-300 ${isDarkMode ? 'bg-gray-800 text-white hover:bg-gray-700' : 'bg-white text-gray-800 hover:bg-gray-50'} shadow-lg`}
          >
            <ArrowLeft className="w-5 h-5" />
            <span>Back to CV Generator</span>
          </Link>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className={`p-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 border ${isDarkMode ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 border-gray-600' : 'bg-white border-gray-200'}`}
          >
            {isDarkMode ? (
              <Sun className="w-6 h-6 text-white" />
            ) : (
              <Moon className="w-6 h-6 text-black" />
            )}
          </button>
        </div>

        {/* Main Content Card */}
        <div className={`rounded-2xl shadow-xl overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-blue-100'} border`}>
          {/* Header */}
          <div className="bg-purple-600 px-6 py-4">
            <div className="flex items-center space-x-3">
              <Target className="w-8 h-8 text-white" />
              <h1 className="text-2xl font-bold text-white">ATS Score Analyzer</h1>
            </div>
            <p className="text-purple-100 mt-2">Upload your CV to get an ATS compatibility score</p>
          </div>

          {/* Upload Section */}
          <div className="p-6">
            <div className="space-y-6">
              {/* File Upload */}
              <div>
                <label className={`block text-lg font-semibold mb-3 transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                  Upload CV (PDF)
                </label>
                <div className="relative">
                  <div className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors duration-300 ${
                    uploadedFile 
                      ? `${isDarkMode ? 'border-green-500 bg-green-900/20' : 'border-green-500 bg-green-50'}` 
                      : `${isDarkMode ? 'border-gray-600 bg-gray-700' : 'border-gray-300 bg-gray-50'}`
                  }`}>
                    {uploadedFile ? (
                      <div className="space-y-3">
                        <FileText className="w-12 h-12 mx-auto text-green-500" />
                        <p className={`font-medium transition-colors duration-300 ${isDarkMode ? 'text-green-300' : 'text-green-700'}`}>
                          {fileName}
                        </p>
                        <p className={`text-sm transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                          File uploaded successfully
                        </p>
                        <button
                          onClick={() => {
                            setUploadedFile(null);
                            setFileName('');
                            setAtsScore(null);
                          }}
                          className={`mt-3 px-4 py-2 rounded-lg transition-colors duration-300 ${isDarkMode ? 'bg-gray-600 text-white hover:bg-gray-500' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
                        >
                          Change File
                        </button>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        <Upload className="w-12 h-12 mx-auto text-gray-400" />
                        <p className={`font-medium transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                          Click to upload or drag and drop
                        </p>
                        <p className={`text-sm transition-colors duration-300 ${isDarkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                          PDF files only
                        </p>
                      </div>
                    )}
                  </div>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                </div>
              </div>

              {/* Analyze Button */}
              <div className="flex justify-center">
                <button
                  onClick={handleAnalyze}
                  disabled={!uploadedFile || isAnalyzing}
                  className="flex items-center space-x-2 bg-purple-600 text-white px-8 py-3 rounded-xl hover:bg-purple-700 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Target className="w-5 h-5" />
                      <span>Analyze ATS Score</span>
                    </>
                  )}
                </button>
              </div>

              {/* Score Display */}
              {atsScore !== null && atsResult && (
                <div className={`mt-8 p-8 rounded-xl border-2 transition-colors duration-300 ${
                  atsScore >= 80 ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-700' :
                  atsScore >= 60 ? 'bg-yellow-50 border-yellow-200 dark:bg-yellow-900/20 dark:border-yellow-700' :
                  'bg-red-50 border-red-200 dark:bg-red-900/20 dark:border-red-700'
                }`}>
                  <div className="text-center space-y-6">
                    {/* Score Icon */}
                    <div className="flex justify-center">
                      {getScoreIcon(atsScore)}
                    </div>

                    {/* Score Percentage */}
                    <div>
                      <h2 className={`text-4xl font-bold mb-2 ${getScoreColor(atsScore)}`}>
                        {atsScore}%
                      </h2>
                      <p className={`text-lg transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        ATS Compatibility Score
                      </p>
                    </div>

                    {/* Progress Meter */}
                    <div className="max-w-md mx-auto">
                      <div className={`w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4 mb-2`}>
                        <div 
                          className={`h-4 rounded-full transition-all duration-1000 ${getScoreBgColor(atsScore)}`}
                          style={{ width: `${atsScore}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className={`transition-colors duration-300 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Poor</span>
                        <span className={`transition-colors duration-300 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Good</span>
                        <span className={`transition-colors duration-300 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>Excellent</span>
                      </div>
                    </div>

                    {/* Score Message */}
                    <p className={`text-lg font-medium ${getScoreColor(atsScore)}`}>
                      {getScoreMessage(atsScore)}
                    </p>

                    {/* Detailed Breakdown */}
                    {atsResult.breakdown && (
                      <div className="mt-6 text-left">
                        <h3 className={`text-lg font-semibold mb-4 transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                          Detailed Analysis
                        </h3>
                        <div className="grid grid-cols-2 gap-4">
                          <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
                            <p className={`text-sm transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Keyword Match</p>
                            <p className="text-lg font-semibold text-blue-600">{atsResult.breakdown.keywordMatch}%</p>
                          </div>
                          <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
                            <p className={`text-sm transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Formatting</p>
                            <p className="text-lg font-semibold text-green-600">{atsResult.breakdown.formatting}%</p>
                          </div>
                          <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
                            <p className={`text-sm transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Structure</p>
                            <p className="text-lg font-semibold text-purple-600">{atsResult.breakdown.structure}%</p>
                          </div>
                          <div className={`p-3 rounded-lg ${isDarkMode ? 'bg-gray-700' : 'bg-gray-100'}`}>
                            <p className={`text-sm transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>Content Quality</p>
                            <p className="text-lg font-semibold text-orange-600">{atsResult.breakdown.contentQuality}%</p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Keywords Found */}
                    {atsResult.keywords.length > 0 && (
                      <div className="mt-6 text-left">
                        <h3 className={`text-lg font-semibold mb-3 transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                          Keywords Found ({atsResult.keywords.length})
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {atsResult.keywords.slice(0, 10).map((keyword, index) => (
                            <span key={index} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                              {keyword}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Suggestions */}
                    {atsResult.suggestions.length > 0 && (
                      <div className="mt-6 text-left">
                        <h3 className={`text-lg font-semibold mb-3 transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
                          Suggestions for Improvement
                        </h3>
                        <ul className="space-y-2">
                          {atsResult.suggestions.map((suggestion, index) => (
                            <li key={index} className={`flex items-start space-x-2 transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                              <span className="text-blue-500 mt-1">•</span>
                              <span>{suggestion}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className={`text-center mt-8 transition-colors duration-300 ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
          <p className="text-sm">
            Upload your CV in PDF format to get an accurate ATS compatibility score
          </p>
        </div>
      </div>
    </div>
  );
} 