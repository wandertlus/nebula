import React, { useState } from 'react';

const SignalInput = ({ onSubmit, isLoading }) => {
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('Work');
  const [priority, setPriority] = useState('medium');
  const [duration, setDuration] = useState(30);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!content.trim()) return;
    
    onSubmit({
      action_text: content,
      category,
      priority,
      duration: parseInt(duration, 10),
      effort_signals: {}
    });
    setContent('');
  };

  return (
    <div className="command-input">
      <div className="cmd-prompt">_&gt;</div>
      
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px', flex: 1 }}>
        
        {/* Main text input */}
        <input
          type="text"
          className="terminal-input"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Inject signal to observatory..."
          disabled={isLoading}
          autoFocus
        />

        {/* Controls row */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ color: 'var(--text-dim)', fontSize: '9px', letterSpacing: '0.3em' }}>CAT</label>
          <select 
            className="terminal-select"
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
            disabled={isLoading}
          >
            <option value="Work">work</option>
            <option value="Education">education</option>
            <option value="Health">health</option>
            <option value="Rest">rest</option>
            <option value="Distraction">distraction</option>
            <option value="space_news">space_news</option>
          </select>

          <label style={{ color: 'var(--text-dim)', fontSize: '9px', letterSpacing: '0.3em' }}>PRI</label>
          <select 
            className="terminal-select"
            value={priority} 
            onChange={(e) => setPriority(e.target.value)}
            disabled={isLoading}
          >
            <option value="high">high</option>
            <option value="medium">medium</option>
            <option value="low">low</option>
          </select>

          <label style={{ color: 'var(--text-dim)', fontSize: '9px', letterSpacing: '0.3em' }}>MIN</label>
          <input
            type="number"
            className="terminal-select"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            min="1"
            max="480"
            style={{ width: '60px', textAlign: 'center' }}
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={isLoading || !content.trim()}
            style={{
              marginLeft: 'auto',
              background: 'transparent',
              border: '1px solid var(--neon-purple)',
              borderRadius: '3px',
              color: isLoading || !content.trim() ? 'var(--text-dim)' : 'var(--neon-purple)',
              fontFamily: 'var(--font-mono)',
              fontSize: '9px',
              letterSpacing: '0.3em',
              padding: '5px 14px',
              cursor: isLoading || !content.trim() ? 'not-allowed' : 'pointer',
              textTransform: 'uppercase',
              transition: 'all 0.2s',
              textShadow: isLoading || !content.trim() ? 'none' : 'var(--glow-text)',
              boxShadow: isLoading || !content.trim() ? 'none' : '0 0 10px rgba(188,19,254,0.2)',
            }}
          >
            {isLoading ? 'processing...' : 'execute ↵'}
          </button>
        </div>
        
      </form>
    </div>
  );
};

export default SignalInput;
