import React, { useState } from 'react';

const SignalInput = ({ onSubmit, isLoading, feedback, onInputChange }) => {
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('Work');
  const [duration, setDuration] = useState(30);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!content.trim()) return;
    
    onSubmit({
      action_text: content,
      category,
      duration: parseInt(duration, 10),
      effort_signals: {}
    });
    setContent('');
  };

  return (
    <div className="command-input">
      <div className="cmd-prompt">_&gt;</div>
      
      <form onSubmit={handleSubmit} className="terminal-form">
        {feedback && (
          <div className={`terminal-feedback ${feedback.type === 'error' ? 'error' : ''}`}>
            {feedback.text}
          </div>
        )}

        <input
          type="text"
          className="terminal-input"
          value={content}
          onChange={(e) => {
            setContent(e.target.value);
            if (onInputChange) onInputChange();
          }}
          placeholder="Inject signal to observatory..."
          disabled={isLoading}
          autoFocus
        />

        <div className="terminal-controls">
          <label className="terminal-label">CAT</label>
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

          <label className="terminal-label">MIN</label>
          <input
            type="number"
            className="terminal-select terminal-duration"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            min="1"
            max="480"
            disabled={isLoading}
          />

          <button
            type="submit"
            className="terminal-submit"
            disabled={isLoading || !content.trim()}
          >
            {isLoading ? 'processing...' : 'execute ↵'}
          </button>
        </div>
        
      </form>
    </div>
  );
};

export default SignalInput;
