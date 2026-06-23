import React from 'react';

const TOPIC_STYLES = {
  Biology: { bg: 'rgba(74, 222, 128, 0.15)', text: '#4ade80', border: 'rgba(74, 222, 128, 0.3)' },
  Physics: { bg: 'rgba(96, 165, 250, 0.15)', text: '#60a5fa', border: 'rgba(96, 165, 250, 0.3)' },
  Chemistry: { bg: 'rgba(251, 191, 36, 0.15)', text: '#fbbf24', border: 'rgba(251, 191, 36, 0.3)' },
  Mathematics: { bg: 'rgba(192, 132, 252, 0.15)', text: '#c084fc', border: 'rgba(192, 132, 252, 0.3)' },
  History: { bg: 'rgba(252, 211, 77, 0.15)', text: '#fcd34d', border: 'rgba(252, 211, 77, 0.3)' },
  Literature: { bg: 'rgba(248, 113, 113, 0.15)', text: '#f87171', border: 'rgba(248, 113, 113, 0.3)' },
  "Computer Science": { bg: 'rgba(45, 212, 191, 0.15)', text: '#2dd4bf', border: 'rgba(45, 212, 191, 0.3)' },
  Economics: { bg: 'rgba(134, 239, 172, 0.15)', text: '#86efac', border: 'rgba(134, 239, 172, 0.3)' },
  Geography: { bg: 'rgba(52, 211, 153, 0.15)', text: '#34d399', border: 'rgba(52, 211, 153, 0.3)' },
  General: { bg: 'var(--bg-tertiary)', text: 'var(--text-secondary)', border: 'var(--border-subtle)' },
};

export default function TopicBadge({ topic }) {
  const style = TOPIC_STYLES[topic] || TOPIC_STYLES.General;
  
  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      gap: '0.35rem',
      padding: '0.2rem 0.6rem',
      borderRadius: '20px',
      fontSize: '0.75rem',
      fontWeight: '600',
      backgroundColor: style.bg,
      color: style.text,
      border: `1px solid ${style.border}`,
      whiteSpace: 'nowrap'
    }}>
      <div style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: style.text }} />
      {topic}
    </span>
  );
}
