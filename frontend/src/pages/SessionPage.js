import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { getSession } from '../services/api';
import useWebSocket from '../hooks/useWebSocket';
import CodeExecutor from '../components/CodeExecutor';
import './SessionPage.css';

const SessionPage = () => {
  const { sessionCode } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [shareLink, setShareLink] = useState('');
  const editorRef = useRef(null);
  const isLocalChange = useRef(false);

  // Initialize share link
  useEffect(() => {
    const link = `${window.location.origin}/session/${sessionCode}`;
    setShareLink(link);
  }, [sessionCode]);

  // Load session data
  useEffect(() => {
    const loadSession = async () => {
      try {
        const sessionData = await getSession(sessionCode);
        setSession(sessionData);
        setCode(sessionData.code || '');
        setLanguage(sessionData.language || 'python');
        setLoading(false);
      } catch (err) {
        setError('Session not found');
        setLoading(false);
      }
    };

    loadSession();
  }, [sessionCode]);

  // WebSocket message handler
  const handleWebSocketMessage = (message) => {
    if (message.type === 'code_update') {
      if (!isLocalChange.current) {
        setCode(message.code);
        if (message.language) {
          setLanguage(message.language);
        }
      }
    } else if (message.type === 'language_update') {
      setLanguage(message.language);
    }
  };

  const { isConnected, sendMessage } = useWebSocket(
    sessionCode,
    handleWebSocketMessage
  );

  // Handle code changes
  const handleCodeChange = (value) => {
    isLocalChange.current = true;
    setCode(value || '');

    // Debounce WebSocket updates
    clearTimeout(handleCodeChange.timeout);
    handleCodeChange.timeout = setTimeout(() => {
      sendMessage({
        type: 'code_change',
        code: value || '',
        language: language,
      });
      isLocalChange.current = false;
    }, 300);
  };

  // Handle language changes
  const handleLanguageChange = (newLanguage) => {
    setLanguage(newLanguage);
    sendMessage({
      type: 'language_change',
      language: newLanguage,
    });
  };

  // Copy share link
  const handleCopyLink = () => {
    navigator.clipboard.writeText(shareLink);
    alert('Link copied to clipboard!');
  };

  const getMonacoLanguage = (lang) => {
    const languageMap = {
      python: 'python',
      javascript: 'javascript',
      java: 'java',
      cpp: 'cpp',
      csharp: 'csharp',
      go: 'go',
      rust: 'rust',
    };
    return languageMap[lang] || 'python';
  };

  if (loading) {
    return (
      <div className="session-page">
        <div className="loading">Loading session...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="session-page">
        <div className="error">{error}</div>
        <button onClick={() => navigate('/')} className="back-button">
          Go Home
        </button>
      </div>
    );
  }

  return (
    <div className="session-page">
      <div className="session-header">
        <div className="session-info">
          <h2>{session?.title || `Session ${sessionCode}`}</h2>
          <div className="session-code">Code: {sessionCode}</div>
        </div>
        <div className="session-controls">
          <div className="connection-status">
            <span
              className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}
            />
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
          <div className="share-section">
            <input
              type="text"
              value={shareLink}
              readOnly
              className="share-input"
            />
            <button onClick={handleCopyLink} className="copy-button">
              Copy Link
            </button>
          </div>
          <select
            value={language}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="language-select"
          >
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
            <option value="csharp">C#</option>
            <option value="go">Go</option>
            <option value="rust">Rust</option>
          </select>
        </div>
      </div>

      <div className="session-content">
        <div className="editor-container">
          <Editor
            height="100%"
            language={getMonacoLanguage(language)}
            value={code}
            onChange={handleCodeChange}
            theme="vs-dark"
            options={{
              minimap: { enabled: true },
              fontSize: 14,
              wordWrap: 'on',
              automaticLayout: true,
            }}
            onMount={(editor) => {
              editorRef.current = editor;
            }}
          />
        </div>

        <div className="executor-container">
          <CodeExecutor code={code} language={language} />
        </div>
      </div>
    </div>
  );
};

export default SessionPage;

