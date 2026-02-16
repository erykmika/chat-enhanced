import { useState } from 'react';
import { register } from '../helpers/api';
import './SignIn.css';

function SignUp({ onGoToSignIn }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await register(email, password);
      // Backend sends a confirmation email; no token to store.
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to sign up. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signin-container">
      <div className="signin-card">
        <h1 className="signin-title">Create account</h1>
        <p className="signin-subtitle">Sign up to get started</p>

        <form onSubmit={handleSubmit} className="signin-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
              disabled={loading || success}
              autoComplete="email"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Create a password"
              required
              disabled={loading || success}
              autoComplete="new-password"
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              required
              disabled={loading || success}
              autoComplete="new-password"
            />
          </div>

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="success-message" role="alert">
              Account created. Please check your email for a confirmation link.
            </div>
          )}

          <button
            type="submit"
            className="signin-button"
            disabled={
              loading ||
              success ||
              !email ||
              !password ||
              !confirmPassword
            }
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>

          {onGoToSignIn && (
            <button
              type="button"
              className="signin-button"
              style={{ marginTop: 10, background: 'transparent', color: '#2563eb', border: '1px solid #d1d5db' }}
              onClick={onGoToSignIn}
              disabled={loading}
            >
              Back to Sign In
            </button>
          )}
        </form>
      </div>
    </div>
  );
}

export default SignUp;
