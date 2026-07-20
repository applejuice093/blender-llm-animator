import { useState } from 'react';

const API_URL = 'http://localhost:8000';

export default function AnimationStudio() {
  const [character, setCharacter] = useState('Aiko');
  const [sceneContext, setSceneContext] = useState('');
  const [requestText, setRequestText] = useState('');
  const [planJson, setPlanJson] = useState('');
  const [compileResult, setCompileResult] = useState('');
  const [status, setStatus] = useState('');

  const handleGeneratePlan = async () => {
    try {
      setStatus('Generating plan...');
      const response = await fetch(`${API_URL}/api/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ character, request_text: requestText, scene_context: sceneContext })
      });
      const data = await response.json();
      if (data.status === 'success') {
        setPlanJson(JSON.stringify(data.plan, null, 2));
        setStatus('Plan generated successfully.');
      } else {
        setStatus(`Error: ${data.detail || 'Failed to generate plan'}`);
      }
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
    }
  };

  const handleCompile = async () => {
    try {
      setStatus('Compiling plan...');
      const parsedPlan = JSON.parse(planJson);
      const response = await fetch(`${API_URL}/api/compile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedPlan)
      });
      const data = await response.json();
      if (data.status === 'success') {
        setCompileResult(data.compiled_script);
        setStatus('Plan compiled successfully.');
      } else {
        setStatus(`Error: ${data.detail || 'Failed to compile plan'}`);
      }
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
    }
  };

  return (
    <div>
      <h1>Animation Studio v1</h1>
      <p style={{ color: 'var(--text-secondary)' }}>
        Describe an animation and generate a structured intent plan, then compile it to Blender code.
      </p>

      <div className="card">
        <h2>1. Request</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <input 
            type="text" 
            placeholder="Character Name (e.g., Aiko)" 
            value={character}
            onChange={(e) => setCharacter(e.target.value)}
          />
          <input 
            type="text" 
            placeholder="Scene Context (e.g., A bright sunny park)" 
            value={sceneContext}
            onChange={(e) => setSceneContext(e.target.value)}
          />
          <textarea 
            rows={3}
            placeholder="Describe the animation... (e.g. 'Make Aiko nervous and wave at the camera')"
            value={requestText}
            onChange={(e) => setRequestText(e.target.value)}
          ></textarea>
          <button onClick={handleGeneratePlan}>Generate Plan</button>
        </div>
      </div>

      {planJson && (
        <div className="card">
          <h2>2. Edit Plan (JSON)</h2>
          <textarea
            rows={15}
            value={planJson}
            onChange={(e) => setPlanJson(e.target.value)}
            style={{ fontFamily: 'monospace', fontSize: '0.9rem' }}
          ></textarea>
          <div style={{ marginTop: '10px' }}>
            <button onClick={handleCompile}>Compile & Execute</button>
          </div>
        </div>
      )}

      {compileResult && (
        <div className="card">
          <h2>3. Compiled Blender Code</h2>
          <pre style={{ 
            backgroundColor: '#2c2c2c', 
            padding: '15px', 
            borderRadius: '4px', 
            overflowX: 'auto',
            fontFamily: 'monospace',
            fontSize: '0.9rem'
          }}>
            {compileResult}
          </pre>
        </div>
      )}

      {status && <div style={{ marginTop: '20px', color: 'var(--accent)' }}>{status}</div>}
    </div>
  );
}
