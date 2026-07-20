import { useState } from 'react'
import './App.css'
import KnowledgeStudio from './components/KnowledgeStudio'
import AnimationStudio from './components/AnimationStudio'
import FineTuningStudio from './components/FineTuningStudio'

function App() {
  const [activeTab, setActiveTab] = useState('finetuning')

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-header">
          Animation Pipeline
        </div>
        <div className="sidebar-nav">
          <div 
            className={`nav-item ${activeTab === 'finetuning' ? 'active' : ''}`}
            onClick={() => setActiveTab('finetuning')}
          >
            Fine-Tuning Studio
          </div>
          <div 
            className={`nav-item ${activeTab === 'knowledge' ? 'active' : ''}`}
            onClick={() => setActiveTab('knowledge')}
          >
            Knowledge Studio (RAG)
          </div>
          <div 
            className={`nav-item ${activeTab === 'blender' ? 'active' : ''}`}
            onClick={() => setActiveTab('blender')}
          >
            Blender Bridge
          </div>
          <div 
            className={`nav-item ${activeTab === 'animation' ? 'active' : ''}`}
            onClick={() => setActiveTab('animation')}
          >
            Animation Studio
          </div>
        </div>
      </div>
      
      <div className="main-content">
        {activeTab === 'knowledge' && <KnowledgeStudio />}
        {activeTab === 'animation' && <AnimationStudio />}
        {activeTab === 'finetuning' && <FineTuningStudio />}
        {activeTab !== 'knowledge' && activeTab !== 'animation' && activeTab !== 'finetuning' && (
          <div className="card">
            <h2>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Studio</h2>
            <p>This module is not yet implemented.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
