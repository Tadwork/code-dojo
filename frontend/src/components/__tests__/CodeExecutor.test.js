import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CodeExecutor from '../CodeExecutor';
import { executeCode } from '../../services/api';

// Mock the API service
jest.mock('../../services/api');

describe('CodeExecutor', () => {
  beforeEach(() => {
    jest.clearAllMocks();
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

  it('should execute JavaScript code via API', async () => {
    executeCode.mockResolvedValueOnce({ output: 'hello', error: '' });

    render(<CodeExecutor code="console.log('hello')" language="javascript" />);

    const runButton = screen.getByText('Run Code');
    fireEvent.click(runButton);

    expect(screen.getByText('Running...')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('hello')).toBeInTheDocument();
    });

    expect(executeCode).toHaveBeenCalledWith("console.log('hello')", 'javascript');
  });

  it('should handle execution errors from API', async () => {
    executeCode.mockResolvedValueOnce({ output: '', error: 'SyntaxError: Unexpected token' });

    render(<CodeExecutor code="invalid code" language="javascript" />);

    const runButton = screen.getByText('Run Code');
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getAllByText(/Error:/i).length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/SyntaxError/i)).toBeInTheDocument();
  });

  it('should handle network errors', async () => {
    executeCode.mockRejectedValueOnce(new Error('Network error'));

    render(<CodeExecutor code="console.log('test')" language="javascript" />);

    const runButton = screen.getByText('Run Code');
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(screen.getAllByText(/Error:/i).length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/Network error/i)).toBeInTheDocument();
  });

  it('should disable run button while executing', async () => {
    // Delay resolution to check disabled state
    executeCode.mockImplementation(() => new Promise(resolve => setTimeout(() => resolve({
      output: 'done',
      error: ''
    }), 100)));

    render(<CodeExecutor code="console.log('test')" language="javascript" />);

    const runButton = screen.getByText('Run Code');
    expect(runButton).not.toBeDisabled();

    fireEvent.click(runButton);

    expect(screen.getByRole('button', { name: /running/i })).toBeDisabled();

    await waitFor(() => {
      expect(screen.getByText('done')).toBeInTheDocument();
    });
  });
});
