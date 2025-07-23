
import { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResult('');
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
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
      if (!response.ok) throw new Error('Extraction failed');
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
