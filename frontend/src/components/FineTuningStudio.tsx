import { useState, useEffect } from 'react';

const API_URL = 'http://localhost:8000';

export default function FineTuningStudio() {
  const [character, setCharacter] = useState('Aiko');
  const [promptsText, setPromptsText] = useState('Make Aiko nervous\nMake Aiko happy and wave');
  const [status, setStatus] = useState('');
  const [datasets, setDatasets] = useState<any[]>([]);
  const [ftStatus, setFtStatus] = useState<any>(null);

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_URL}/api/finetune/status`);
      const data = await res.json();
      if (data.status === 'success') {
        setFtStatus(data.data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchDatasets = async () => {
    try {
      const res = await fetch(`${API_URL}/api/dataset/list`);
      const data = await res.json();
      if (data.status === 'success') {
        setDatasets(data.datasets);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchDatasets();
    checkStatus();
  }, []);

  const [sceneContext, setSceneContext] = useState('');

  const handleGenerate = async () => {
    try {
      setStatus('Generating dataset with 3-step Critique... This will take 3x longer.');
      const prompts = promptsText.split('\n').filter(p => p.trim() !== '');
      const response = await fetch(`${API_URL}/api/dataset/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ character, prompts, scene_context: sceneContext })
      });
      const data = await response.json();
      if (data.status === 'success') {
        setStatus(`Generated batch ${data.data.batch_id} with ${data.data.successful}/${data.data.total} successful plans.`);
        fetchDatasets();
      } else {
        setStatus(`Error: ${data.detail || 'Failed'}`);
      }
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
    }
  };

  return (
    <div>
      <h1>Fine-Tuning Studio (Dataset Factory)</h1>
      <p style={{ color: 'var(--text-secondary)' }}>
        Generate synthetic <code>(Prompt) &rarr; (JSON Plan)</code> training pairs using Ollama to build your fine-tuning dataset.
      </p>

      <div className="card">
        <h2>1. Batch Generator</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <input 
            type="text" 
            placeholder="Character" 
            value={character}
            onChange={(e) => setCharacter(e.target.value)}
          />
          <input 
            type="text" 
            placeholder="Scene Context (e.g., Dark alley, raining)" 
            value={sceneContext}
            onChange={(e) => setSceneContext(e.target.value)}
          />
          <textarea 
            rows={5}
            placeholder="Enter one prompt per line..."
            value={promptsText}
            onChange={(e) => setPromptsText(e.target.value)}
          ></textarea>
          <button onClick={handleGenerate}>Generate Dataset</button>
        </div>
        {status && <div style={{ marginTop: '10px', color: 'var(--accent)' }}>{status}</div>}
      </div>

      <div className="card">
        <h2>2. Generated Datasets</h2>
        {datasets.length === 0 ? (
          <p>No datasets found.</p>
        ) : (
          <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ borderBottom: '1px solid #444', padding: '8px' }}>Filename</th>
                <th style={{ borderBottom: '1px solid #444', padding: '8px' }}>Records</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((d, i) => (
                <tr key={i}>
                  <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{d.filename}</td>
                  <td style={{ padding: '8px', borderBottom: '1px solid #333' }}>{d.record_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>3. Training Dashboard</h2>
        <p>To start training, open your WSL terminal in the backend directory and run:</p>
        <pre style={{ backgroundColor: '#2c2c2c', padding: '15px', borderRadius: '4px' }}>
          python finetune.py
        </pre>
        <button onClick={checkStatus} style={{ marginTop: '10px' }}>Refresh Status</button>
        
        {ftStatus && (
          <div style={{ marginTop: '15px', padding: '10px', backgroundColor: '#222', borderRadius: '4px' }}>
            <div><strong>LoRA Adapters Generated:</strong> {ftStatus.lora_output_exists ? '✅ Yes' : '❌ No'}</div>
            <div><strong>GGUF Merged for Ollama:</strong> {ftStatus.gguf_exists ? '✅ Yes' : '❌ No'}</div>
            {ftStatus.gguf_file && (
              <div style={{ color: 'var(--accent)' }}>File: {ftStatus.gguf_file}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
