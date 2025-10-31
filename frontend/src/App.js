import { useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Landing Page Component
const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <div className="landing-content">
        <div className="logo-section">
          <div className="visa-logo">VISA</div>
        </div>
        
        <h1 className="main-title">
          Women's World Cup 2023
          <br />
          <span className="highlight">Small Business Grant Program</span>
        </h1>
        
        <p className="subtitle">
          Creating a visual story of Visa's $500,000 commitment to empowering
          <br />
          women entrepreneurs through sports
        </p>
        
        <button 
          className="cta-button"
          onClick={() => navigate('/generator')}
        >
          Generate Infographic
          <svg className="arrow-icon" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
        
        <div className="info-cards">
          <div className="info-card">
            <div className="info-icon">💰</div>
            <h3>$500K</h3>
            <p>Total Funding</p>
          </div>
          <div className="info-card">
            <div className="info-icon">⚽</div>
            <h3>64 Matches</h3>
            <p>Grant Opportunities</p>
          </div>
          <div className="info-card">
            <div className="info-icon">🇨🇦</div>
            <h3>Canada</h3>
            <p>Indigenous Women Focus</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Generator Page Component
const GeneratorPage = () => {
  const [loading, setLoading] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [error, setError] = useState(null);
  const [loadingMessage, setLoadingMessage] = useState("");

  const generateInfographic = async () => {
    setLoading(true);
    setError(null);
    setGeneratedImage(null);
    setLoadingMessage("Preparing your infographic...");

    try {
      // Simulate loading states
      setTimeout(() => setLoadingMessage("Analyzing data and structure..."), 2000);
      setTimeout(() => setLoadingMessage("Creating visual design with Visa blue theme..."), 5000);
      setTimeout(() => setLoadingMessage("Finalizing your infographic..."), 10000);

      const response = await axios.post(`${API}/generate-infographic`);
      
      if (response.data && response.data.image_base64) {
        setGeneratedImage(response.data.image_base64);
        setLoadingMessage("");
      } else {
        throw new Error("No image data received");
      }
    } catch (err) {
      console.error("Error generating infographic:", err);
      setError(
        err.response?.data?.detail || 
        err.message || 
        "Failed to generate infographic. Please try again."
      );
      setLoadingMessage("");
    } finally {
      setLoading(false);
    }
  };

  const downloadImage = () => {
    if (!generatedImage) return;

    const link = document.createElement('a');
    link.href = generatedImage;
    link.download = 'visa-wwc-infographic.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="generator-page">
      <div className="generator-header">
        <div className="visa-logo-small">VISA</div>
        <h1>Infographic Generator</h1>
      </div>

      <div className="generator-content">
        <div className="info-section">
          <h2>Program Details</h2>
          
          <div className="detail-group">
            <h3>🏆 Visa Player of the Match Grant</h3>
            <ul>
              <li><strong>Year:</strong> 2023 (FIFA Women's World Cup Australia & New Zealand 2023™)</li>
              <li><strong>Total Funding:</strong> $500,000 USD globally</li>
              <li><strong>Innovation:</strong> First time the Visa Player of the Match award was linked to a grant</li>
            </ul>
          </div>

          <div className="detail-group">
            <h3>⚽ How It Worked</h3>
            <ul>
              <li>After each of the <strong>64 matches</strong>, the female small business owner from the same country as the winning Player of the Match received a grant</li>
              <li>Grant amounts ranged from <strong>$5,000 USD</strong> (group-stage) to <strong>$50,000 USD</strong> (Final)</li>
            </ul>
          </div>

          <div className="detail-group">
            <h3>🇨🇦 Canadian Partnership</h3>
            <ul>
              <li>Visa partnered with the <strong>Canadian Council of Aboriginal Business (CCAB)</strong></li>
              <li>When a Canadian player won Player of the Match, funds were granted to the CCAB</li>
              <li><strong>Purpose:</strong> Support Indigenous women entrepreneurs</li>
            </ul>
          </div>

          <div className="detail-group context-note">
            <h3>📊 Canada's She's Next Program Context</h3>
            <p>
              Canada's repositioned grant offering through CCAB demonstrates Visa's commitment 
              to supporting underrepresented entrepreneurs. The She's Next program focuses on 
              providing resources and funding to women-owned small businesses, and the WWC 2023 
              partnership extended this mission to specifically support Indigenous women entrepreneurs.
            </p>
          </div>

          {!generatedImage && (
            <button 
              className="generate-button"
              onClick={generateInfographic}
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Generate Infographic'}
            </button>
          )}
        </div>

        <div className="output-section">
          {loading && (
            <div className="loading-container">
              <div className="spinner"></div>
              <p className="loading-text">{loadingMessage}</p>
              <p className="loading-subtext">This may take up to 60 seconds...</p>
            </div>
          )}

          {error && (
            <div className="error-container">
              <div className="error-icon">⚠️</div>
              <h3>Generation Failed</h3>
              <p>{error}</p>
              <button className="retry-button" onClick={generateInfographic}>
                Try Again
              </button>
            </div>
          )}

          {generatedImage && !loading && (
            <div className="result-container">
              <h3>Your Infographic</h3>
              <div className="image-wrapper">
                <img 
                  src={generatedImage} 
                  alt="Visa Women's World Cup Infographic" 
                  className="generated-image"
                />
              </div>
              <div className="action-buttons">
                <button className="download-button" onClick={downloadImage}>
                  <svg className="download-icon" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                  Download PNG
                </button>
                <button className="regenerate-button" onClick={generateInfographic}>
                  Generate New
                </button>
              </div>
            </div>
          )}

          {!loading && !error && !generatedImage && (
            <div className="placeholder-container">
              <div className="placeholder-icon">🎨</div>
              <p>Your infographic will appear here</p>
              <p className="placeholder-subtext">Click "Generate Infographic" to create</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/generator" element={<GeneratorPage />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
