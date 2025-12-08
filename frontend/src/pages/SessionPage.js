import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { getSession, generateCode } from '../services/api';
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

  // AI Assistant state
  const [aiPrompt, setAiPrompt] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

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

  // AI Code Generation
  const handleGenerateCode = async () => {
    if (!aiPrompt.trim()) return;

    setAiLoading(true);
    setAiError('');

    try {
      const result = await generateCode(aiPrompt, code, language);
      if (result.error) {
        setAiError(result.error);
      } else if (result.code) {
        // Update code and sync via WebSocket
        setCode(result.code);
        sendMessage({
          type: 'code_change',
          code: result.code,
          language: language,
        });
        setAiPrompt(''); // Clear prompt on success
      }
    } catch (err) {
      setAiError(err.response?.data?.detail || 'Failed to generate code');
    } finally {
      setAiLoading(false);
    }
  };

  const getMonacoLanguage = (lang) => {
    // Map our language identifiers to Monaco language IDs
    const languageMap = {
      python: 'python',
      javascript: 'javascript',
      typescript: 'typescript',
      java: 'java',
      c: 'c',
      cpp: 'cpp',
      csharp: 'csharp',
      go: 'go',
      rust: 'rust',
      ruby: 'ruby',
      php: 'php',
      swift: 'swift',
      kotlin: 'kotlin',
      scala: 'scala',
      bash: 'shell',
      perl: 'perl',
      lua: 'lua',
      r: 'r',
      dart: 'dart',
      elixir: 'elixir',
      clojure: 'clojure',
      haskell: 'haskell',
      julia: 'julia',
      pascal: 'pascal',
      fsharp: 'fsharp',
      nim: 'nim',
      crystal: 'ruby', // Crystal syntax is similar to Ruby
      sql: 'sql',
      powershell: 'powershell',
      erlang: 'erlang',
      fortran: 'fortran',
      cobol: 'cobol',
      prolog: 'prolog',
      lisp: 'scheme', // Use scheme for lisp-like syntax
      ocaml: 'ocaml',
      groovy: 'groovy',
      d: 'd',
      zig: 'zig',
    };
    return languageMap[lang] || 'plaintext';
  };

  // Language options organized by category
  const languageOptions = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'c', label: 'C' },
    { value: 'cpp', label: 'C++' },
    { value: 'csharp', label: 'C#' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'ruby', label: 'Ruby' },
    { value: 'php', label: 'PHP' },
    { value: 'swift', label: 'Swift' },
    { value: 'kotlin', label: 'Kotlin' },
    { value: 'scala', label: 'Scala' },
    { value: 'bash', label: 'Bash' },
    { value: 'perl', label: 'Perl' },
    { value: 'lua', label: 'Lua' },
    { value: 'r', label: 'R' },
    { value: 'dart', label: 'Dart' },
    { value: 'elixir', label: 'Elixir' },
    { value: 'clojure', label: 'Clojure' },
    { value: 'haskell', label: 'Haskell' },
    { value: 'julia', label: 'Julia' },
    { value: 'pascal', label: 'Pascal' },
    { value: 'fsharp', label: 'F#' },
    { value: 'nim', label: 'Nim' },
    { value: 'crystal', label: 'Crystal' },
    { value: 'sql', label: 'SQL' },
    { value: 'powershell', label: 'PowerShell' },
    { value: 'erlang', label: 'Erlang' },
    { value: 'fortran', label: 'Fortran' },
    { value: 'cobol', label: 'COBOL' },
    { value: 'prolog', label: 'Prolog' },
    { value: 'lisp', label: 'Lisp' },
    { value: 'ocaml', label: 'OCaml' },
    { value: 'groovy', label: 'Groovy' },
    { value: 'd', label: 'D' },
    { value: 'zig', label: 'Zig' },
  ];

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
            {languageOptions.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* AI Assistant Panel */}
      <div className="ai-assistant-panel">
        <div className="ai-assistant-input-group">
          <span className="ai-icon">✨</span>
          <input
            type="text"
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !aiLoading && handleGenerateCode()}
            placeholder="Ask AI to generate or modify code... (e.g., 'Add a function to sort an array')"
            className="ai-prompt-input"
            disabled={aiLoading}
          />
          <button
            onClick={handleGenerateCode}
            disabled={aiLoading || !aiPrompt.trim()}
            className="ai-generate-button"
          >
            {aiLoading ? 'Generating...' : 'Generate'}
          </button>
        </div>
        {aiError && <div className="ai-error">{aiError}</div>}
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
