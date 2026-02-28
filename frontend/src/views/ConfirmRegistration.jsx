import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { confirmRegistration } from '../helpers/api';
import './SignIn.css';

function ConfirmRegistration() {
  const { token } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const emailFromQuery = useMemo(() => searchParams.get('email') || '', [searchParams]);

  const [email, setEmail] = useState(emailFromQuery);
  const [status, setStatus] = useState('idle'); // idle | loading | success | error
  const [error, setError] = useState('');

  useEffect(() => {
    setEmail(emailFromQuery);
  }, [emailFromQuery]);

  const canSubmit = Boolean(email) && Boolean(token) && status !== 'loading' && status !== 'success';

  const doConfirm = async (e) => {
    e?.preventDefault?.();
    setError('');

    if (!token) {
      setStatus('error');
      setError('Missing confirmation token.');
      return;
    }

    if (!email) {
      setStatus('error');
      setError('Missing email. Please enter the email you registered with.');
      return;
    }

    setStatus('loading');
    try {
      await confirmRegistration(email, token);
      setStatus('success');
      // Small delay so the user sees success.
      setTimeout(() => navigate('/'), 1000);
    } catch (err) {
      setStatus('error');
      setError(err.message || 'Confirmation failed.');
    }
  };

  return (
    <div className="signin-container">
      <div className="signin-card">
        <h1 className="signin-title">Confirm your account</h1>
        <p className="signin-subtitle">Finish setting up your account</p>

        <form onSubmit={doConfirm} className="signin-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter the email you registered with"
              required
              disabled={status === 'loading' || status === 'success'}
              autoComplete="email"
            />
          </div>

          {status === 'success' && (
            <div className="success-message" role="alert">
              Account confirmed. Redirecting to sign in…
            </div>
          )}

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          <button type="submit" className="signin-button" disabled={!canSubmit}>
            {status === 'loading' ? 'Confirming…' : 'Confirm account'}
          </button>

          <button
            type="button"
            className="signin-button"
            style={{ marginTop: 10, background: 'transparent', color: '#2563eb', border: '1px solid #d1d5db' }}
            onClick={() => navigate('/')}
            disabled={status === 'loading'}
          >
            Back to Sign In
          </button>
        </form>
      </div>
    </div>
  );
}

export default ConfirmRegistration;

