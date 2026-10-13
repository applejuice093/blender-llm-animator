import { useState } from 'react';
import { postJson } from '../api';

export default function KnowledgeStudio() {
  const [addContent, setAddContent] = useState('');
  const [docId, setDocId] = useState('');
  const [addStatus, setAddStatus] = useState('');
  
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any>(null);
  const [queryStatus, setQueryStatus] = useState('');

  const handleAdd = async () => {
    try {
      setAddStatus('Adding...');
      const data = await postJson<{ doc_id: string }>('/api/knowledge/add', {
        content: addContent,
        doc_id: docId || undefined,
      });
      setAddStatus(`Success! Document ID: ${data.doc_id}`);
      setAddContent('');
      setDocId('');
    } catch (e: unknown) {
      setAddStatus(`Error: ${e instanceof Error ? e.message : String(e)}`);
    }
  };

  const handleQuery = async () => {
    try {
      setQueryStatus('Searching...');
      const data = await postJson('/api/knowledge/query', { query });
      setResults(data);
      setQueryStatus('Complete');
    } catch (e: unknown) {
      setQueryStatus(`Error: ${e instanceof Error ? e.message : String(e)}`);
    }
  };

  return (
    <div>
      <h1>Knowledge Studio (RAG)</h1>
      <p style={{ color: 'var(--text-secondary)' }}>
        Manage rig capability summaries and character profiles.
      </p>

      <div className="card">
        <h2>Add to Knowledge Base</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <input 
            type="text" 
            placeholder="Document ID (Optional, e.g., 'aiko_rig')" 
            value={docId}
            onChange={(e) => setDocId(e.target.value)}
          />
          <textarea 
            rows={6}
            placeholder="Paste rig manifest, capability summary, or personality sheet here..."
            value={addContent}
            onChange={(e) => setAddContent(e.target.value)}
          ></textarea>
          <button onClick={handleAdd}>Add Document</button>
          {addStatus && <div style={{ marginTop: '10px', fontSize: '0.9rem' }}>{addStatus}</div>}
        </div>
      </div>

      <div className="card">
        <h2>Query Knowledge Base</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', gap: '10px' }}>
            <input 
              type="text" 
              placeholder="e.g., 'What are Aiko's rig capabilities?'"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
            />
            <button onClick={handleQuery}>Search</button>
          </div>
          {queryStatus && <div style={{ fontSize: '0.9rem' }}>{queryStatus}</div>}
          
          {results && results.documents && results.documents[0] && (
            <div style={{ marginTop: '20px' }}>
              <h3>Results:</h3>
              {results.documents[0].map((doc: string, idx: number) => (
                <div key={idx} style={{ 
                  backgroundColor: '#2c2c2c', 
                  padding: '10px', 
                  borderRadius: '4px',
                  marginBottom: '10px',
                  borderLeft: '4px solid var(--accent)'
                }}>
                  <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '5px' }}>
                    Distance (lower = closer): {results.distances[0][idx].toFixed(4)} | ID: {results.ids[0][idx]}
                  </div>
                  <div>{doc}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
