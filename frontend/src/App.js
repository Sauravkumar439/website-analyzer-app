import React, { useState } from 'react';
import './App.css';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

function App() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeWebsite = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://website-analyzer-app-production.up.railway.app/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error analyzing website:', error);
    }
    setLoading(false);
  };

  const downloadPDF = () => {
    const report = document.getElementById('report');
    html2canvas(report).then((canvas) => {
      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF();
      const imgProps = pdf.getImageProperties(imgData);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
      pdf.save('website-report.pdf');
    });
  };

  return (
    <div className="App">
      <h1>Website Analyzer</h1>
      <input
        type="text"
        value={url}
        placeholder="Enter website URL"
        onChange={(e) => setUrl(e.target.value)}
      />
      <button onClick={analyzeWebsite}>Analyze</button>

      {loading && <p>Analyzing...</p>}

      {result && result.status === 'success' && (
        <div id="report">
          <h2>Results:</h2>
          <p><strong>Title:</strong> {result.title}</p>
          <p><strong>Meta Description:</strong> {result.meta_description}</p>
          <p><strong>Word Count:</strong> {result.word_count}</p>
          <p><strong>Content Quality:</strong> {result.content_status}</p>
          <p><strong>Originality Score:</strong> {result.originality_score}%</p>
          <p><strong>AdSense Found:</strong> {result.adsense_found ? 'Yes' : 'No'}</p>
          <p><strong>Duplicate Paragraphs:</strong> {result.duplicate_content ? 'Yes' : 'No'}</p>
          <p><strong>H1 Tags:</strong> {result.h1_count}</p>
          <p><strong>H2 Tags:</strong> {result.h2_count}</p>
          <p><strong>Images Without Alt:</strong> {result.images_without_alt}</p>

          {result.matching_sources && result.matching_sources.length > 0 && (
            <div>
              <h3>Matching Snippets:</h3>
              <ul>
                {result.matching_sources.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {result && result.status === 'success' && (
        <button onClick={downloadPDF} style={{ marginTop: '10px' }}>
          Download Report as PDF
        </button>
      )}
    </div>
  );
}

export default App;
