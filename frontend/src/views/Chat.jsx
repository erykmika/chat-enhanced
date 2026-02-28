import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchChatUsers, getAccessToken, getWsBaseUrl } from '../helpers/api';
import './Chat.css';

function Chat() {
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [messagesByUser, setMessagesByUser] = useState({});
  const [draft, setDraft] = useState('');
  const [status, setStatus] = useState('disconnected');
  const [error, setError] = useState('');
  const [onlineUsers, setOnlineUsers] = useState({});
  const wsRef = useRef(null);

  const appendMessage = useCallback((partner, message) => {
    setMessagesByUser((prev) => {
      const existing = prev[partner] || [];
      return {
        ...prev,
        [partner]: [...existing, message],
      };
    });
  }, []);

  const activeMessages = useMemo(() => {
    if (!selectedUser) {
      return [];
    }

    return messagesByUser[selectedUser.email] || [];
  }, [messagesByUser, selectedUser]);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      navigate('/');
      return;
    }

    fetchChatUsers(token)
      .then((response) => {
        setUsers(response.users || []);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load users.');
      });
  }, [navigate]);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      return undefined;
    }

    const wsUrl = `${getWsBaseUrl()}?token=${encodeURIComponent(token)}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setStatus('connected');
      ws.send(JSON.stringify({ type: 'list_users' }));
    };

    ws.onclose = () => {
      setStatus('disconnected');
    };

    ws.onerror = () => {
      setError('Websocket connection error.');
    };

    ws.onmessage = (event) => {
      let payload;
      try {
        payload = JSON.parse(event.data);
      } catch {
        return;
      }

      if (!payload || typeof payload !== 'object') {
        return;
      }

      if (payload.type === 'message') {
        const sender = payload.from;
        if (typeof sender !== 'string' || !sender) {
          return;
        }

        appendMessage(sender, {
          from: sender,
          content: payload.content,
          timestamp: payload.timestamp,
        });
      }

      if (payload.type === 'user_list') {
        const userMap = {};
        (payload.users || []).forEach((user) => {
          if (user && user.email) {
            userMap[user.email] = Boolean(user.online);
          }
        });
        setOnlineUsers(userMap);
      }

      if (payload.type === 'user_status') {
        if (payload.email) {
          setOnlineUsers((prev) => ({
            ...prev,
            [payload.email]: Boolean(payload.online),
          }));
        }
      }
    };

    return () => {
      ws.close();
    };
  }, [appendMessage]);

  const handleSend = () => {
    if (!selectedUser || !draft.trim()) {
      return;
    }

    const outgoing = {
      type: 'message',
      to: selectedUser.email,
      content: draft.trim(),
    };

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(outgoing));
    }

    appendMessage(selectedUser.email, {
      from: 'me',
      content: draft.trim(),
      timestamp: new Date().toISOString(),
    });

    setDraft('');
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/');
  };

  return (
    <div className="chat-layout">
      <aside className="chat-sidebar">
        <div className="chat-sidebar-header">
          <h2>Chats</h2>
          <button type="button" onClick={handleLogout} className="chat-logout">
            Log out
          </button>
        </div>
        {error && <div className="chat-error">{error}</div>}
        <div className="chat-status">WS: {status}</div>
        <ul className="chat-user-list">
          {users.map((user) => (
            <li key={user.email}>
              <button
                type="button"
                className={
                  selectedUser?.email === user.email
                    ? 'chat-user active'
                    : 'chat-user'
                }
                onClick={() => setSelectedUser(user)}
              >
                <span>{user.email}</span>
                <span className={onlineUsers[user.email] ? 'chat-pill online' : 'chat-pill'}>
                  {onlineUsers[user.email] ? 'online' : 'offline'}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <section className="chat-main">
        <div className="chat-header">
          {selectedUser ? (
            <>
              <h3>{selectedUser.email}</h3>
              <span className={onlineUsers[selectedUser.email] ? 'chat-pill online' : 'chat-pill'}>
                {onlineUsers[selectedUser.email] ? 'online' : 'offline'}
              </span>
            </>
          ) : (
            <h3>Select a user to start chatting</h3>
          )}
        </div>

        <div className="chat-messages">
          {activeMessages.map((message, index) => (
            <div
              key={`${message.timestamp || 'ts'}-${index}`}
              className={
                message.from === 'me'
                  ? 'chat-message outgoing'
                  : 'chat-message incoming'
              }
            >
              <div className="chat-bubble">
                <p>{message.content}</p>
                {message.timestamp && (
                  <span className="chat-timestamp">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="chat-composer">
          <input
            type="text"
            placeholder={
              selectedUser ? 'Type a message...' : 'Select a user to start chatting'
            }
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            disabled={!selectedUser}
            onKeyDown={(event) => {
              if (event.key === 'Enter') {
                handleSend();
              }
            }}
          />
          <button type="button" onClick={handleSend} disabled={!selectedUser || !draft.trim()}>
            Send
          </button>
        </div>
      </section>
    </div>
  );
}

export default Chat;

