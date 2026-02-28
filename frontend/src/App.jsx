import { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import SignIn from './views/SignIn'
import SignUp from './views/SignUp'
import ConfirmRegistration from './views/ConfirmRegistration'
import './App.css'

function RootAuth() {
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

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RootAuth />} />
        <Route path="/confirm/:token" element={<ConfirmRegistration />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
