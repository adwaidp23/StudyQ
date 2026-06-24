import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiFetch } from '../api';
import { History as HistoryIcon, Filter, Inbox, ChevronDown, ChevronUp, BrainCircuit } from 'lucide-react';
import TopicBadge from './TopicBadge';

export default function History() {
  const [filter, setFilter] = useState('');
  const [expanded, setExpanded] = useState({});

  const { data: topics = [] } = useQuery({
    queryKey: ['topics'],
    queryFn: () => apiFetch('/topics')
  });

  const { data: questions = [], isLoading } = useQuery({
    queryKey: ['history', filter],
    queryFn: () => {
      const qsPath = filter ? `/questions?topic=${encodeURIComponent(filter)}` : '/questions';
      return apiFetch(qsPath);
    }
  });

  const toggleExpand = (id) => {
    setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const formatDate = (dateStr) => {
    return new Date(dateStr + "Z").toLocaleDateString(undefined, {
      month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
    });
  };

  return (
    <div className="glass-card animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <HistoryIcon className="text-gradient" size={24} />
          Study History
        </h2>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <Filter size={16} style={{ color: 'var(--text-tertiary)' }} />
        <button 
          onClick={() => setFilter('')}
          style={{
            padding: '0.4rem 1rem', borderRadius: '20px', fontSize: '0.85rem', fontWeight: '500',
            background: filter === '' ? 'var(--accent-glow)' : 'var(--bg-tertiary)',
            color: filter === '' ? 'var(--accent-primary)' : 'var(--text-secondary)',
            border: `1px solid ${filter === '' ? 'var(--accent-primary)' : 'var(--border-subtle)'}`
          }}
        >
          All Topics
        </button>
        {topics.map(t => (
          <button 
            key={t}
            onClick={() => setFilter(t)}
            style={{
              padding: '0.4rem 1rem', borderRadius: '20px', fontSize: '0.85rem', fontWeight: '500',
              background: filter === t ? 'var(--accent-glow)' : 'var(--bg-tertiary)',
              color: filter === t ? 'var(--accent-primary)' : 'var(--text-secondary)',
              border: `1px solid ${filter === t ? 'var(--accent-primary)' : 'var(--border-subtle)'}`
            }}
          >
            {t}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem 0' }}>
          <div className="spinner" />
        </div>
      ) : questions.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-tertiary)' }}>
          <Inbox size={48} style={{ margin: '0 auto 1rem', opacity: 0.5 }} />
          <p>{filter ? `No questions found for "${filter}"` : 'Your history is empty. Ask your first question!'}</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {questions.map(q => (
            <div key={q.id} style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '1.25rem', transition: 'border-color 0.2s' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '1rem', marginBottom: '1rem' }}>
                <h3 style={{ fontSize: '1.05rem', fontWeight: '500', lineHeight: 1.4 }}>{q.text}</h3>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem', flexShrink: 0 }}>
                  <TopicBadge topic={q.topic} />
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>{formatDate(q.created_at)}</span>
                </div>
              </div>

              {q.agent_response && (
                <div style={{ background: 'var(--bg-tertiary)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem', borderLeft: '3px solid var(--accent-primary)' }}>
                   <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-primary)', marginBottom: '0.5rem', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    <BrainCircuit size={14} className="text-gradient" /> Agentic Summary
                  </h4>
                  <div style={{ whiteSpace: 'pre-wrap', color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.5' }}>
                    {q.agent_response}
                  </div>
                </div>
              )}

              {q.similar && q.similar.length > 0 && (
                <div>
                  <button 
                    onClick={() => toggleExpand(q.id)}
                    className="btn-ghost"
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 0', fontSize: '0.85rem' }}
                  >
                    {expanded[q.id] ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    {expanded[q.id] ? 'Hide Similar' : `View ${q.similar.length} Similar Question${q.similar.length !== 1 ? 's' : ''}`}
                  </button>
                  
                  {expanded[q.id] && (
                    <div className="animate-fade-in" style={{ marginTop: '0.5rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                      {q.similar.map(s => (
                        <div key={s.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-tertiary)', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)' }}>
                          <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>{s.text}</p>
                          <TopicBadge topic={s.topic} />
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
