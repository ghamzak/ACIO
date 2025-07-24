
import { useState } from 'react';
import './App.css';


function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [provider, setProvider] = useState('openai');
  const [predictedType, setPredictedType] = useState('');
  const [feedback, setFeedback] = useState(null); // 'up' | 'down' | null
  const [correction, setCorrection] = useState('');
  // Full contract types list from backend config
  const contractTypes = [
    "Director Service Agreement",
    "Employment Contract",
    "Employee Transfer Agreement",
    "Independent Contractor Agreement",
    "Non-Compete Agreement",
    "Recruitment Contract",
    "Termination Agreement",
    "Cloud Computing Agreement",
    "Equipment Lease Agreement",
    "Non-Disclosure Agreement (NDA)",
    "Property Lease Agreement",
    "Security Agreement",
    "Terms of Use",
    "Advisory Agreement",
    "Confidentiality Agreement",
    "Influencer Agreement",
    "Photography Release",
    "Privacy Agreement",
    "Purchase Order",
    "Renewal Order",
    "Sales Contract",
    "Vendor Agreement",
    "Warranty Contract",
    "Contract Amendment",
    "Joint Venture (JV) Contract",
    "License Agreement",
    "Master Service Agreement (MSA)",
    "Memorandum of Understanding (MOU)",
    "Partnership Agreement",
    "Promissory Note",
    "Statement of Work (SOW)"
  ];

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
    'image/jpeg',
    'image/png',
  ];

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setError('');
    setPredictedType('');
    setFeedback(null);
    setCorrection('');
    if (!selected) {
      setFile(null);
      return;
    }
    if (!ALLOWED_TYPES.includes(selected.type)) {
      setError('Unsupported file type. Please upload PDF, DOCX, JPG, or PNG.');
      setFile(null);
      return;
    }
    if (selected.size > MAX_FILE_SIZE) {
      setError('File is too large. Maximum allowed size is 10MB.');
      setFile(null);
      return;
    }
    setFile(selected);
  };

  const handleProviderChange = (e) => {
    setProvider(e.target.value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    setLoading(true);
    setError('');
    setPredictedType('');
    setFeedback(null);
    setCorrection('');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch(`http://localhost:8000/classify-contract/?provider=${provider}`, {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Classification failed');
      }
      const data = await response.json();
      setPredictedType(data.contract_type || 'Unknown');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = (type) => {
    setFeedback(type);
    if (type === 'up') {
      setCorrection('');
    }
  };

  const handleCorrectionChange = (e) => {
    setCorrection(e.target.value);
  };

  return (
    <div className="container">
      <h1>Contract Type Classifier</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf,.docx,.jpg,.jpeg,.png" onChange={handleFileChange} />
        <select value={provider} onChange={handleProviderChange} style={{ marginLeft: 8 }}>
          <option value="openai">OpenAI</option>
          <option value="groq">Groq</option>
        </select>
        <button type="submit" disabled={loading || !file} style={{ marginLeft: 8 }}>
          {loading ? 'Classifying...' : 'Upload & Classify'}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      {predictedType && (
        <div className="result">
          <h2>Predicted Contract Type</h2>
          <div style={{ fontSize: '1.2em', fontWeight: 'bold', marginBottom: 8 }}>{predictedType}</div>
          <div>
            <span>Is this correct? </span>
            <button
              style={{ marginRight: 8, color: feedback === 'up' ? 'green' : undefined }}
              onClick={() => handleFeedback('up')}
              disabled={feedback === 'up'}
            >
              👍
            </button>
            <button
              style={{ color: feedback === 'down' ? 'red' : undefined }}
              onClick={() => handleFeedback('down')}
              disabled={feedback === 'down'}
            >
              👎
            </button>
          </div>
          {feedback === 'down' && (
            <div style={{ marginTop: 12 }}>
              <label htmlFor="correction">Select correct contract type: </label>
              <select id="correction" value={correction} onChange={handleCorrectionChange}>
                <option value="">--Choose--</option>
                {contractTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              {correction && (
                <div style={{ marginTop: 8, color: 'blue' }}>
                  You selected: <b>{correction}</b>
                </div>
              )}
            </div>
          )}
          {feedback === 'up' && (
            <div style={{ marginTop: 12, color: 'green' }}>Thank you for your feedback!</div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
