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
      if (language === 'javascript') {
        await executeJavaScript(code);
      } else if (language === 'python') {
        await executePython(code);
      } else {
        setError('Unsupported language. Only Python and JavaScript are supported.');
        setIsRunning(false);
      }
    } catch (err) {
      setError(err.message || 'Execution error');
      setIsRunning(false);
    }
  };

  const executeJavaScript = async (codeToRun) => {
    // Use Web Worker for safer execution
    const workerCode = `
      self.onmessage = function(e) {
        try {
          const code = e.data;
          let output = '';
          const originalLog = console.log;
          const originalError = console.error;
          
          console.log = function(...args) {
            output += args.map(arg => 
              typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
            ).join(' ') + '\\n';
          };
          
          console.error = function(...args) {
            output += 'ERROR: ' + args.map(arg => 
              typeof arg === 'object' ? JSON.stringify(arg, null, 2) : String(arg)
            ).join(' ') + '\\n';
          };
          
          // Execute code with timeout
          const startTime = Date.now();
          const timeout = 5000; // 5 seconds
          
          try {
            eval(code);
            const endTime = Date.now();
            if (endTime - startTime > timeout) {
              throw new Error('Execution timeout');
            }
          } catch (err) {
            throw err;
          }
          
          self.postMessage({ type: 'output', data: output || '(no output)' });
        } catch (error) {
          self.postMessage({ type: 'error', data: error.message });
        }
      };
    `;

    const blob = new Blob([workerCode], { type: 'application/javascript' });
    const worker = new Worker(URL.createObjectURL(blob));
    workerRef.current = worker;

    worker.onmessage = (e) => {
      if (e.data.type === 'output') {
        setOutput(e.data.data);
        setIsRunning(false);
      } else if (e.data.type === 'error') {
        setError(e.data.data);
        setIsRunning(false);
      }
      terminateWorker();
    };

    worker.onerror = (err) => {
      setError(`Execution error: ${err.message}`);
      setIsRunning(false);
      terminateWorker();
    };

    worker.postMessage(codeToRun);
  };

  const executePython = async (codeToRun) => {
    // For Python, we'll use Pyodide (WebAssembly Python)
    // For now, show a message that Python execution requires additional setup
    try {
      // Try to load Pyodide if available
      if (window.pyodide) {
        const result = await window.pyodide.runPython(codeToRun);
        setOutput(String(result || '(no output)'));
      } else {
        // Fallback: show instructions
        setOutput('Python execution requires Pyodide. Loading...');
        
        // Dynamically load Pyodide
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js';
        script.onload = async () => {
          window.pyodide = await window.loadPyodide({
            indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.24.1/full/',
          });
          
          try {
            window.pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
            `);
            
            window.pyodide.runPython(codeToRun);
            const stdout = window.pyodide.runPython('sys.stdout.getvalue()');
            setOutput(stdout || '(no output)');
          } catch (err) {
            setError(err.message || 'Python execution error');
          }
          setIsRunning(false);
        };
        script.onerror = () => {
          setError('Failed to load Pyodide. Python execution is not available.');
          setIsRunning(false);
        };
        document.head.appendChild(script);
      }
    } catch (err) {
      setError(err.message || 'Python execution error');
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

