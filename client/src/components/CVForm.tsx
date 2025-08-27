'use client';

import { useState } from 'react';
import { Download, FileText, Trash2, Type, Moon, Sun, FileDown, Target } from 'lucide-react';
import Link from 'next/link';
import { useTheme } from '@/contexts/ThemeContext';
import { config } from '@/lib/config';

const initialState = {
  cvContent: ''
};

export default function CVForm() {
  const [formData, setFormData] = useState(initialState);
  const [jsonData, setJsonData] = useState('');
  const [textSize, setTextSize] = useState(16);
  const [isLoading, setIsLoading] = useState(false);
  const { isDarkMode, toggleTheme } = useTheme();

  const handleChange = (e: { target: { name: any; value: any; }; }) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleGenerate = async () => {
    if (!formData.cvContent.trim()) {
      alert('Please enter some CV content first');
      return;
    }

    setIsLoading(true);
    try {
      // Call the backend /generate-cv-json endpoint directly
      const response = await fetch(`${config.BACKEND_URL}${config.ENDPOINTS.GENERATE_CV_JSON}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          cv_text: formData.cvContent
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate JSON: ${errorText}`);
      }

      const data = await response.json();
      
      if (data.success && data.json) {
        setJsonData(JSON.stringify(data.json, null, 2));
      } else {
        throw new Error(data.error || 'Failed to generate structured JSON');
      }
    } catch (error) {
      console.error('Error generating CV JSON:', error);
      alert('Failed to generate CV JSON. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = () => {
    const cvData = {
      content: formData.cvContent,
      generatedAt: new Date().toISOString(),
      wordCount: formData.cvContent.split(' ').filter(word => word.length > 0).length
    };
    
    const blob = new Blob([JSON.stringify(cvData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'cv-data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = async () => {
    if (!formData.cvContent.trim()) {
      alert('Please enter CV content first');
      return;
    }

    setIsLoading(true);
    try {
      // Call the backend /download-cv-pdf endpoint directly
      const response = await fetch(`${config.BACKEND_URL}${config.ENDPOINTS.DOWNLOAD_CV_PDF}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          cv_text: formData.cvContent
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to generate PDF: ${errorText}`);
      }

      // Get the PDF blob
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cv.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to download PDF. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setFormData(initialState);
    setJsonData('');
  };

  const adjustTextSize = (delta: number) => {
    setTextSize(prev => Math.max(12, Math.min(24, prev + delta)));
  };

  const wordCount = formData.cvContent.split(' ').filter(word => word.length > 0).length;

  return (
    <div className={`min-h-screen transition-colors duration-300 ${isDarkMode ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900' : 'bg-gradient-to-br from-blue-50 via-white to-blue-100'}`}>
      <div className="container mx-auto px-4 py-4 max-w-8xl">
        {/* Theme Toggle Button */}
        <div className="absolute top-4 right-4">
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
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <FileText className="w-8 h-8 text-white" />
          </div>
          <h1 className={`text-4xl font-bold mb-2 transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
            ATS-Compatible CV Generator
          </h1>
          <p className={`text-lg transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
            Create your professional CV with our AI-powered tool
          </p>
        </div>

        {/* Main Content Card */}
        <div className={`rounded-2xl shadow-xl overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-blue-100'} border`}>
          {/* Text Size Controls */}
          <div className={`px-6 py-4 border-b transition-colors duration-300 ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-blue-50 border-blue-100'}`}>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div className="flex items-center space-x-3">
                <Type className="w-5 h-5 text-blue-600" />
                <span className={`font-medium transition-colors duration-300 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>Text Size:</span>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => adjustTextSize(-2)}
                    className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 transition-colors"
                  >
                    -
                  </button>
                  <span className={`w-12 text-center font-medium transition-colors duration-300 ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>
                    {textSize}px
                  </span>
                  <button
                    onClick={() => adjustTextSize(2)}
                    className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 transition-colors"
                  >
                    +
                  </button>
                </div>
              </div>
              <div className={`text-sm transition-colors duration-300 ${isDarkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                Words: <span className="font-semibold text-blue-600">{wordCount}</span>
              </div>
            </div>
          </div>

          {/* Text Input Area */}
          <div className="p-6">
            <label className={`block text-lg font-semibold mb-3 transition-colors duration-300 ${isDarkMode ? 'text-white' : 'text-gray-800'}`}>
              CV Content
            </label>
            <textarea
              name="cvContent"
              value={formData.cvContent}
              onChange={handleChange}
              placeholder={config.DEFAULT_CV_TEMPLATE}
              className={`w-full p-4 border-2 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 outline-none transition-all duration-200 resize-y ${isDarkMode ? 'border-gray-600 text-white bg-gray-700' : 'border-blue-200 text-black bg-white'}`}
              rows={15}
              style={{ fontSize: `${textSize}px`, lineHeight: '1.6' }}
            />
          </div>

          {/* Action Buttons */}
          <div className={`px-6 py-4 border-t transition-colors duration-300 ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-50 border-gray-200'}`}>
            <div className="flex flex-wrap gap-3 justify-center sm:justify-start">
              <button
                onClick={handleGenerate}
                disabled={isLoading}
                className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <FileText className="w-5 h-5" />
                    <span>Generate JSON</span>
                  </>
                )}
              </button>
              
              <button
                onClick={handleDownloadPDF}
                disabled={!formData.cvContent.trim() || isLoading}
                className="flex items-center space-x-2 bg-green-600 text-white px-6 py-3 rounded-xl hover:bg-green-700 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Downloading...</span>
                  </>
                ) : (
                  <>
                    <FileDown className="w-5 h-5" />
                    <span>Download PDF</span>
                  </>
                )}
              </button>
              
              <Link
                href="/ats-score"
                className="flex items-center space-x-2 bg-purple-600 text-white px-6 py-3 rounded-xl hover:bg-purple-700 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 duration-200"
              >
                <Target className="w-5 h-5" />
                <span>Get ATS Score</span>
              </Link>
              
              <button
                onClick={handleClear}
                className="flex items-center space-x-2 bg-red-500 text-white px-6 py-3 rounded-xl hover:bg-red-600 transition-colors shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 duration-200"
              >
                <Trash2 className="w-5 h-5" />
                <span>Clear</span>
              </button>
            </div>
          </div>
        </div>

        {/* JSON Output */}
        {jsonData && (
          <div className={`mt-8 rounded-2xl shadow-xl border overflow-hidden transition-colors duration-300 ${isDarkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-blue-100'}`}>
            <div className="bg-blue-600 px-6 py-4">
              <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
                <FileText className="w-5 h-5" />
                <span>Generated JSON Data</span>
              </h2>
            </div>
            <div className="p-6">
              <pre className={`p-4 rounded-xl text-sm overflow-x-auto border whitespace-pre-wrap transition-colors duration-300 ${isDarkMode ? 'bg-gray-700 border-gray-600 text-gray-200' : 'bg-gray-50 border-gray-200 text-gray-800'}`}>
                {jsonData}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}