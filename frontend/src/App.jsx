
import { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');


  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
    'image/jpeg',
    'image/png',
  ];

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setResult('');
    setError('');
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    setLoading(true);
    setResult('');
    setError('');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('http://localhost:8000/extract-text/', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Extraction failed');
      }
      const data = await response.json();
      setResult(data.text);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>Contract Text Extractor</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".pdf,.docx,.jpg,.jpeg,.png" onChange={handleFileChange} />
        <button type="submit" disabled={loading || !file}>
          {loading ? 'Extracting...' : 'Upload & Extract'}
        </button>
      </form>
      {error && <div className="error">{error}</div>}
      {result && (
        <div className="result">
          <h2>Extracted Text</h2>
          <pre>{result}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
