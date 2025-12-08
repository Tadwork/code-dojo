import React, { useState, useRef, useEffect } from 'react';
import './CodeExecutor.css';

const CodeExecutor = ({ code, language }) => {
  const [output, setOutput] = useState('');
  const [error, setError] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const workerRef = useRef(null);

  const terminateWorker = () => {
    if (workerRef.current && typeof workerRef.current.terminate === 'function') {
      workerRef.current.terminate();
    }
    workerRef.current = null;
  };

  useEffect(() => {
    // Cleanup worker on unmount
    return () => {
      terminateWorker();
    };
  }, []);

  const executeCode = async () => {
    setIsRunning(true);
    setOutput('');
    setError('');

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, language }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      if (data.error) {
        setError(data.error);
      }
      setOutput(data.output);

    } catch (err) {
      setError(err.message || 'Execution error');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="code-executor">
      <div className="executor-header">
        <h3>Code Output</h3>
        <button
          onClick={executeCode}
          disabled={isRunning}
          className="run-button"
        >
          {isRunning ? 'Running...' : 'Run Code'}
        </button>
      </div>
      <div className="executor-content">
        {error && (
          <div className="executor-error">
            <strong>Error:</strong> {error}
          </div>
        )}
        <pre className="executor-output">
          {output || (error ? '' : 'Click "Run Code" to execute your code')}
        </pre>
      </div>
    </div>
  );
};

export default CodeExecutor;

