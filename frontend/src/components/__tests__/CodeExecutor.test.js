import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import CodeExecutor from '../CodeExecutor';

// Mock Web Worker
global.Worker = jest.fn(() => ({
  postMessage: jest.fn(),
  terminate: jest.fn(),
  onmessage: null,
  onerror: null,
}));

global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
global.URL.revokeObjectURL = jest.fn();

// Mock Pyodide
global.window.pyodide = null;
global.window.loadPyodide = jest.fn();

describe('CodeExecutor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    global.Worker.mockClear();
  });

  it('should render code executor component', () => {
    render(<CodeExecutor code="console.log('hello')" language="javascript" />);

    expect(screen.getByText('Code Output')).toBeInTheDocument();
    expect(screen.getByText('Run Code')).toBeInTheDocument();
  });

  it('should display placeholder text initially', () => {
    render(<CodeExecutor code="" language="javascript" />);

    expect(
      screen.getByText('Click "Run Code" to execute your code')
    ).toBeInTheDocument();
  });

  it('should execute JavaScript code', async () => {
    const mockWorker = {
      postMessage: jest.fn(),
      terminate: jest.fn(),
      onmessage: null,
      onerror: null,
    };

    global.Worker.mockImplementation(() => mockWorker);

    render(<CodeExecutor code="console.log('hello')" language="javascript" />);

    const runButton = screen.getByText('Run Code');
    fireEvent.click(runButton);

    expect(screen.getByText('Running...')).toBeInTheDocument();
    expect(mockWorker.postMessage).toHaveBeenCalledWith("console.log('hello')");

    // Simulate worker response
    await act(async () => {
      mockWorker.onmessage({ data: { type: 'output', data: 'hello\n' } });
    });

    await waitFor(() => {
      expect(screen.getByText('hello')).toBeInTheDocument();
    });
  });

  it('should handle JavaScript execution errors', async () => {
    const mockWorker = {
      postMessage: jest.fn(),
      terminate: jest.fn(),
      onmessage: null,
      onerror: null,
    };

    global.Worker.mockImplementation(() => mockWorker);

    render(<CodeExecutor code="invalid code" language="javascript" />);

    const runButton = screen.getByText('Run Code');
    fireEvent.click(runButton);

    // Simulate worker error
    await act(async () => {
      mockWorker.onmessage({
        data: { type: 'error', data: 'SyntaxError: Unexpected token' },
      });
    });

    await waitFor(() => {
      expect(screen.getAllByText(/Error:/i).length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/SyntaxError/i)).toBeInTheDocument();
  });

  it('should show error for unsupported languages', async () => {
    render(<CodeExecutor code="print('hello')" language="java" />);

    const runButton = screen.getByText('Run Code');
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(
        screen.getByText(/Code execution for java is not yet supported/i)
      ).toBeInTheDocument();
    });
  });

  it('should disable run button while executing', () => {
    render(<CodeExecutor code="console.log('test')" language="javascript" />);

    const runButton = screen.getByText('Run Code');
    expect(runButton).not.toBeDisabled();

    fireEvent.click(runButton);

    expect(screen.getByRole('button', { name: /running/i })).toBeDisabled();
  });

  it('should cleanup worker on unmount', () => {
    const mockWorker = {
      postMessage: jest.fn(),
      terminate: jest.fn(),
      onmessage: null,
      onerror: null,
    };

    global.Worker.mockImplementation(() => mockWorker);

    const { unmount } = render(
      <CodeExecutor code="console.log('test')" language="javascript" />
    );

    const runButton = screen.getByText('Run Code');
    fireEvent.click(runButton);

    unmount();

    expect(mockWorker.terminate).toHaveBeenCalled();
  });
});

