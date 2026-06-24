import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiFetch } from '../api';
import { Search, Sparkles, CheckCircle2, X, BrainCircuit } from 'lucide-react';
import TopicBadge from './TopicBadge';

export default function Ask() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: async (questionText) => {
      return apiFetch('/questions', {
        method: 'POST',
        body: JSON.stringify({ text: questionText.trim() })
      });
    },
    onSuccess: (data) => {
      setResult(data);
      setText('');
      // Invalidate history query to refetch data
      queryClient.invalidateQueries({ queryKey: ['history'] });
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    mutation.mutate(text);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }} className="animate-fade-in">
      <div className="glass-card">
        <h2 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Sparkles className="text-gradient" size={24} />
          Ask an AI Tutor
        </h2>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          Type your question below. Our Agentic AI will generate a structured explanation and link related past queries.
        </p>

        <form onSubmit={handleSubmit}>
          <textarea
            className="input-field"
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="e.g. Why does photosynthesis require sunlight?&#10;How does Newton's second law relate to acceleration?"
            style={{ minHeight: '120px', resize: 'vertical', marginBottom: '0.5rem' }}
            maxLength={1000}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{text.length}/1000</span>
            <button type="submit" className="btn-primary" disabled={mutation.isPending || !text.trim()}>
              {mutation.isPending ? <div className="spinner" /> : <><Search size={18} /> Ask AI</>}
            </button>
          </div>
          {mutation.isError && (
            <div style={{ color: 'var(--danger-text)', marginTop: '1rem', fontSize: '0.875rem' }}>
              {mutation.error?.message || 'Failed to submit question'}
            </div>
          )}
        </form>
      </div>

      {result && (
        <div className="glass-card animate-fade-in" style={{ borderLeft: '4px solid var(--success-text)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success-text)', fontWeight: '600' }}>
              <CheckCircle2 size={20} /> Question Answered
            </div>
            <button onClick={() => setResult(null)} className="btn-ghost" style={{ padding: '0.25rem' }}><X size={20} /></button>
          </div>
          
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>{result.text}</h3>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Topic:</span>
            <TopicBadge topic={result.topic} />
          </div>

          {result.agent_response && (
            <div style={{ background: 'var(--bg-tertiary)', padding: '1.25rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)', marginBottom: '1.5rem' }}>
              <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)', marginBottom: '0.75rem' }}>
                <BrainCircuit size={18} className="text-gradient" /> Agentic Analysis
              </h4>
              <div style={{ whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: '1.6' }}>
                {result.agent_response}
              </div>
            </div>
          )}

          {result.similar?.length > 0 && (
            <div style={{ paddingTop: '1.5rem', borderTop: '1px solid var(--border-subtle)' }}>
              <h4 style={{ color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', fontSize: '0.75rem', marginBottom: '1rem' }}>
                {result.similar.length} Similar Reference Questions
              </h4>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {result.similar.map(s => (
                  <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', background: 'var(--bg-tertiary)', padding: '1rem', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                    <div>
                      <p style={{ marginBottom: '0.5rem', fontSize: '0.95rem' }}>{s.text}</p>
                      <TopicBadge topic={s.topic} />
                    </div>
                    <div style={{ background: 'var(--success-bg)', color: 'var(--success-text)', border: '1px solid var(--success-border)', padding: '0.25rem 0.5rem', borderRadius: 'var(--radius-sm)', fontSize: '0.75rem', fontWeight: '700', flexShrink: 0 }}>
                      {Math.round(s.similarity * 100)}% Match
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
