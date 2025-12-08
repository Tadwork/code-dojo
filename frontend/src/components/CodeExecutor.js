import React, { useState, useRef, useEffect } from 'react';
import { executeCode as executeCodeFromAPI } from '../services/api';
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
      console.log('Calling executeCode service...');
      const data = await executeCodeFromAPI(code, language);
      console.log('Received data from service:', data);

      if (!data) {
        throw new Error('No data received from server');
      }

      if (data.error) {
        setError(data.error);
      }
      setOutput(data.output);

    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Execution error');
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

