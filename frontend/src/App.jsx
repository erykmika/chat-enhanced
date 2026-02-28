import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, useNavigate } from 'react-router-dom'
import SignIn from './views/SignIn'
import SignUp from './views/SignUp'
import ConfirmRegistration from './views/ConfirmRegistration'
import Chat from './views/Chat'
import './App.css'

function RootAuth() {
  const [view, setView] = useState('signin')
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      navigate('/chat')
    }
  }, [navigate])

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
        <Route path="/chat" element={<Chat />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
