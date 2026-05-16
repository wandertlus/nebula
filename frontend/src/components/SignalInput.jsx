import React, { useState } from 'react';
import { Send } from 'lucide-react';

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
    <div className="glass-panel" style={{ marginTop: 'auto' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--text-main)', marginBottom: '8px' }}>Inject Signal</h3>
        
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
          <input
            type="text"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What action did you complete?"
            style={{
              flex: 1,
              minWidth: '250px',
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '12px 16px',
              color: 'var(--text-main)',
              fontFamily: 'var(--font-body)',
              fontSize: '1rem',
              outline: 'none'
            }}
            disabled={isLoading}
          />
          
          <select 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
            style={{
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '12px 16px',
              color: 'var(--text-main)',
              fontFamily: 'var(--font-body)',
              outline: 'none',
              cursor: 'pointer'
            }}
            disabled={isLoading}
          >
            <option value="Work">Work</option>
            <option value="Education">Education</option>
            <option value="Health">Health</option>
            <option value="space_news">Space News</option>
            <option value="Rest">Rest</option>
            <option value="Distraction">Distraction</option>
          </select>

          <select 
            value={priority} 
            onChange={(e) => setPriority(e.target.value)}
            style={{
              background: 'rgba(0,0,0,0.3)',
              border: '1px solid var(--border-color)',
              borderRadius: '8px',
              padding: '12px 16px',
              color: 'var(--text-main)',
              fontFamily: 'var(--font-body)',
              outline: 'none',
              cursor: 'pointer'
            }}
            disabled={isLoading}
          >
            <option value="high">High Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="low">Low Priority</option>
          </select>

          <div style={{ display: 'flex', alignItems: 'center', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '0 16px' }}>
            <input
              type="number"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              min="1"
              style={{
                width: '60px',
                background: 'transparent',
                border: 'none',
                color: 'var(--text-main)',
                fontFamily: 'var(--font-body)',
                fontSize: '1rem',
                outline: 'none'
              }}
              disabled={isLoading}
            />
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>min</span>
          </div>

          <button 
            type="submit"
            disabled={isLoading || !content.trim()}
            style={{
              background: isLoading ? 'var(--border-color)' : 'var(--neon-purple)',
              border: 'none',
              borderRadius: '8px',
              padding: '12px 24px',
              color: 'white',
              fontFamily: 'var(--font-heading)',
              fontWeight: 600,
              cursor: isLoading || !content.trim() ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'opacity 0.2s'
            }}
          >
            {isLoading ? 'Processing...' : 'Execute'} <Send size={16} />
          </button>
        </div>
      </form>
    </div>
  );
};

export default SignalInput;
