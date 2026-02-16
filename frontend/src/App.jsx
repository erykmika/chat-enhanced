import { useState } from 'react'
import SignIn from './views/SignIn'
import SignUp from './views/SignUp'
import './App.css'

function App() {
  const [view, setView] = useState('signin')

  if (view === 'signup') {
    return <SignUp onGoToSignIn={() => setView('signin')} />
  }

  return (
    <div>
      <SignIn />
      <div style={{ marginTop: 12, textAlign: 'center' }}>
        <button
          type="button"
          onClick={() => setView('signup')}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#2563eb',
            cursor: 'pointer',
            textDecoration: 'underline',
          }}
        >
          Create an account
        </button>
      </div>
    </div>
  )
}

export default App
