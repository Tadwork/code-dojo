import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import SessionPage from '../SessionPage';
import * as api from '../../services/api';
import useWebSocket from '../../hooks/useWebSocket';

jest.mock('../../services/api');
jest.mock('../../hooks/useWebSocket');
jest.mock('@monaco-editor/react', () => ({
  __esModule: true,
  default: ({ value, onChange }) => (
    <textarea
      data-testid="monaco-editor"
      value={value}
      onChange={(e) => onChange && onChange(e.target.value)}
    />
  ),
}));

const mockSession = {
  id: 'test-id',
  session_code: 'TEST1234',
  title: 'Test Session',
  language: 'python',
  code: 'print("hello")',
  created_at: '2024-01-01T00:00:00',
  active_users: 0,
};

const renderWithRouter = (component, initialEntries = ['/session/TEST1234']) => {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <Routes>
        <Route path="/session/:sessionCode" element={component} />
      </Routes>
    </MemoryRouter>
  );
};

describe('SessionPage', () => {
  const mockSendMessage = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useWebSocket.mockReturnValue({
      isConnected: true,
      sendMessage: mockSendMessage,
    });
    global.navigator.clipboard = {
      writeText: jest.fn().mockResolvedValue(),
    };
    global.alert = jest.fn();
  });

  it('should show loading state initially', () => {
    api.getSession.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    renderWithRouter(<SessionPage />);

    expect(screen.getByText('Loading session...')).toBeInTheDocument();
  });

  it('should load and display session data', async () => {
    api.getSession.mockResolvedValue(mockSession);

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByText('Test Session')).toBeInTheDocument();
      expect(screen.getByText(/Code: TEST1234/i)).toBeInTheDocument();
    });
  });

  it('should display error when session not found', async () => {
    api.getSession.mockRejectedValue(new Error('Session not found'));

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByText('Session not found')).toBeInTheDocument();
    });
  });

  it('should display share link', async () => {
    api.getSession.mockResolvedValue(mockSession);

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      const shareInput = screen.getByDisplayValue(
        /http:\/\/localhost(:3000)?\/session\/TEST1234/i
      );
      expect(shareInput).toBeInTheDocument();
    });
  });

  it('should copy share link to clipboard', async () => {
    api.getSession.mockResolvedValue(mockSession);

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      const copyButton = screen.getByText('Copy Link');
      fireEvent.click(copyButton);

      expect(navigator.clipboard.writeText).toHaveBeenCalled();
      expect(global.alert).toHaveBeenCalledWith('Link copied to clipboard!');
    });
  });

  it('should display connection status', async () => {
    api.getSession.mockResolvedValue(mockSession);
    useWebSocket.mockReturnValue({
      isConnected: true,
      sendMessage: mockSendMessage,
    });

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });
  });

  it('should allow changing language', async () => {
    api.getSession.mockResolvedValue(mockSession);

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      const languageSelect = screen.getByRole('combobox');
      expect(languageSelect.value).toBe('python');
      fireEvent.change(languageSelect, { target: { value: 'javascript' } });

      expect(mockSendMessage).toHaveBeenCalledWith({
        type: 'language_change',
        language: 'javascript',
      });
    });
  });

  it('should handle code changes', async () => {
    api.getSession.mockResolvedValue(mockSession);
    jest.useFakeTimers();

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      const editor = screen.getByTestId('monaco-editor');
      fireEvent.change(editor, { target: { value: 'new code' } });

      jest.advanceTimersByTime(300);

      expect(mockSendMessage).toHaveBeenCalledWith({
        type: 'code_change',
        code: 'new code',
        language: 'python',
      });
    });

    jest.useRealTimers();
  });

  it('should render CodeExecutor component', async () => {
    api.getSession.mockResolvedValue(mockSession);

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByText('Code Output')).toBeInTheDocument();
    });
  });
});

