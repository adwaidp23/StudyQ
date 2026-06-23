import React, { useState } from 'react';
import { apiFetch } from '../api';
import { LogIn, UserPlus } from 'lucide-react';

export default function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const res = await apiFetch(endpoint, {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      
      localStorage.setItem('studyq_token', res.token);
      onLogin(res.email);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '80vh' }}>
      <div className="glass-card animate-fade-in" style={{ width: '100%', maxWidth: '420px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 className="text-gradient" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>StudyQ</h1>
          <p style={{ color: 'var(--text-secondary)' }}>AI-powered semantic question search</p>
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', background: 'var(--bg-tertiary)', padding: '0.25rem', borderRadius: 'var(--radius-sm)' }}>
          <button 
            onClick={() => { setIsLogin(true); setError(''); }}
            style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', background: isLogin ? 'var(--surface-glass)' : 'transparent', color: isLogin ? 'var(--text-primary)' : 'var(--text-secondary)' }}
          >
            Sign In
          </button>
          <button 
            onClick={() => { setIsLogin(false); setError(''); }}
            style={{ flex: 1, padding: '0.5rem', borderRadius: '4px', background: !isLogin ? 'var(--surface-glass)' : 'transparent', color: !isLogin ? 'var(--text-primary)' : 'var(--text-secondary)' }}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label className="form-label">Email</label>
            <input 
              type="email" 
              className="input-field" 
              placeholder="you@example.com" 
              value={email} 
              onChange={e => setEmail(e.target.value)}
              required 
            />
          </div>
          <div>
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder={isLogin ? "••••••••" : "Min 6 characters"} 
              value={password} 
              onChange={e => setPassword(e.target.value)}
              required 
            />
          </div>
          
          {error && <div style={{ color: 'var(--danger-text)', fontSize: '0.875rem', marginTop: '0.5rem' }}>{error}</div>}
          
          <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '0.5rem' }}>
            {loading ? <div className="spinner" /> : (
              <>
                {isLogin ? <LogIn size={18} /> : <UserPlus size={18} />}
                {isLogin ? 'Sign In' : 'Create Account'}
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
