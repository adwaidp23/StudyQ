import React, { useState, useEffect } from 'react';
import Auth from './components/Auth';
import Ask from './components/Ask';
import History from './components/History';
import { LogOut, BookOpen } from 'lucide-react';

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('ask');

  useEffect(() => {
    const token = localStorage.getItem('studyq_token');
    const email = localStorage.getItem('studyq_email');
    if (token && email) {
      setUser(email);
    }
  }, []);

  const handleLogin = (email) => {
    localStorage.setItem('studyq_email', email);
    setUser(email);
  };

  const handleLogout = () => {
    localStorage.removeItem('studyq_token');
    localStorage.removeItem('studyq_email');
    setUser(null);
    setActiveTab('ask');
  };

  if (!user) {
    return (
      <div className="app-container">
        <Auth onLogin={handleLogin} />
      </div>
    );
  }

  return (
    <div className="app-container">
      <nav style={{ 
        background: 'var(--surface-glass)', 
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border-subtle)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        padding: '1rem 1.5rem'
      }}>
        <div style={{ maxWidth: '900px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ background: 'linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))', padding: '0.5rem', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <BookOpen size={20} color="white" />
            </div>
            <span style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em' }}>
              Study<span className="text-gradient">Q</span>
            </span>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
            <div style={{ display: 'flex', background: 'var(--bg-tertiary)', padding: '0.25rem', borderRadius: 'var(--radius-sm)' }}>
              <button 
                onClick={() => setActiveTab('ask')}
                style={{ padding: '0.4rem 1rem', borderRadius: '4px', fontSize: '0.9rem', fontWeight: '500', background: activeTab === 'ask' ? 'var(--surface-glass)' : 'transparent', color: activeTab === 'ask' ? 'var(--text-primary)' : 'var(--text-secondary)' }}
              >
                Ask
              </button>
              <button 
                onClick={() => setActiveTab('history')}
                style={{ padding: '0.4rem 1rem', borderRadius: '4px', fontSize: '0.9rem', fontWeight: '500', background: activeTab === 'history' ? 'var(--surface-glass)' : 'transparent', color: activeTab === 'history' ? 'var(--text-primary)' : 'var(--text-secondary)' }}
              >
                History
              </button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', paddingLeft: '1.5rem', borderLeft: '1px solid var(--border-subtle)' }}>
              <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{user}</span>
              <button onClick={handleLogout} className="btn-ghost" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.4rem 0.75rem' }}>
                <LogOut size={16} /> <span style={{ fontSize: '0.85rem' }}>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="main-content">
        {activeTab === 'ask' ? <Ask /> : <History />}
      </main>
    </div>
  );
}

export default App;
