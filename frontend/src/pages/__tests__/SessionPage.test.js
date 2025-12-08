import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import SessionPage from '../SessionPage';
import * as api from '../../services/api';
import useWebSocket from '../../hooks/useWebSocket';

jest.mock('../../services/api');
jest.mock('../../hooks/useWebSocket');
jest.mock('../../utils/participantUtils', () => ({
  hexToRgba: (hex, alpha) => `rgba(0, 0, 0, ${alpha})`,
}));
jest.mock('@monaco-editor/react', () => ({
  __esModule: true,
  default: ({ value, onChange, onMount }) => {
    // Simulate editor mount
    if (onMount) {
      const mockEditor = {
        onDidChangeCursorPosition: jest.fn(),
        onDidChangeCursorSelection: jest.fn(),
        deltaDecorations: jest.fn(() => []),
      };
      const mockMonaco = {
        Range: jest.fn(),
        editor: {
          TrackedRangeStickiness: { NeverGrowsWhenTypingAtEdges: 1 },
        },
      };
      onMount(mockEditor, mockMonaco);
    }
    return (
      <textarea
        data-testid="monaco-editor"
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
      />
    );
  },
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
  const mockSendCursorPosition = jest.fn();
  const mockSendSelection = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    useWebSocket.mockReturnValue({
      isConnected: true,
      sendMessage: mockSendMessage,
      sendCursorPosition: mockSendCursorPosition,
      sendSelection: mockSendSelection,
      participants: {},
      myInfo: { userId: 'test-user', displayName: 'Test User', color: '#FF6B6B' },
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
    });
    expect(screen.getByText(/Code: TEST1234/i)).toBeInTheDocument();
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
      expect(screen.getByText('Copy Link')).toBeInTheDocument();
    });
    const copyButton = screen.getByText('Copy Link');
    fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalled();
    expect(global.alert).toHaveBeenCalledWith('Link copied to clipboard!');
  });

  it('should display connection status', async () => {
    api.getSession.mockResolvedValue(mockSession);
    useWebSocket.mockReturnValue({
      isConnected: true,
      sendMessage: mockSendMessage,
      sendCursorPosition: mockSendCursorPosition,
      sendSelection: mockSendSelection,
      participants: {},
      myInfo: { userId: 'test-user', displayName: 'Test User', color: '#FF6B6B' },
    });

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByText('Connected')).toBeInTheDocument();
    });
  });

  it('should show participant names in the participants panel', async () => {
    api.getSession.mockResolvedValue(mockSession);
    useWebSocket.mockReturnValue({
      isConnected: true,
      sendMessage: mockSendMessage,
      sendCursorPosition: mockSendCursorPosition,
      sendSelection: mockSendSelection,
      participants: {
        'other-user': { userId: 'other-user', displayName: 'Other User', color: '#123456' },
      },
      myInfo: { userId: 'test-user', displayName: 'Test User', color: '#FF6B6B' },
    });

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByText('Other User')).toBeInTheDocument();
    });
    expect(screen.getByText('O')).toBeInTheDocument();
  });

  it('should allow changing language', async () => {
    api.getSession.mockResolvedValue(mockSession);

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByRole('combobox')).toBeInTheDocument();
    });
    const languageSelect = screen.getByRole('combobox');
    expect(languageSelect.value).toBe('python');
    fireEvent.change(languageSelect, { target: { value: 'javascript' } });

    expect(mockSendMessage).toHaveBeenCalledWith({
      type: 'language_change',
      language: 'javascript',
    });
  });

  it('should handle code changes', async () => {
    api.getSession.mockResolvedValue(mockSession);
    jest.useFakeTimers();

    renderWithRouter(<SessionPage />);

    await waitFor(() => {
      expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
    });
    const editor = screen.getByTestId('monaco-editor');
    fireEvent.change(editor, { target: { value: 'new code' } });

    jest.advanceTimersByTime(300);

    expect(mockSendMessage).toHaveBeenCalledWith({
      type: 'code_change',
      code: 'new code',
      language: 'python',
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

  describe('AI Assistant', () => {
    it('should render AI assistant panel', async () => {
      api.getSession.mockResolvedValue(mockSession);

      renderWithRouter(<SessionPage />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Ask AI to generate/i)).toBeInTheDocument();
      });
      expect(screen.getByText('Generate')).toBeInTheDocument();
    });

    it('should allow entering AI prompt', async () => {
      api.getSession.mockResolvedValue(mockSession);

      renderWithRouter(<SessionPage />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Ask AI to generate/i)).toBeInTheDocument();
      });

      const promptInput = screen.getByPlaceholderText(/Ask AI to generate/i);
      fireEvent.change(promptInput, { target: { value: 'Create a hello function' } });

      expect(promptInput.value).toBe('Create a hello function');
    });

    it('should disable generate button when prompt is empty', async () => {
      api.getSession.mockResolvedValue(mockSession);

      renderWithRouter(<SessionPage />);

      await waitFor(() => {
        expect(screen.getByText('Generate')).toBeInTheDocument();
      });

      const generateButton = screen.getByText('Generate');
      expect(generateButton).toBeDisabled();
    });

    it('should enable generate button when prompt has content', async () => {
      api.getSession.mockResolvedValue(mockSession);

      renderWithRouter(<SessionPage />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Ask AI to generate/i)).toBeInTheDocument();
      });

      const promptInput = screen.getByPlaceholderText(/Ask AI to generate/i);
      fireEvent.change(promptInput, { target: { value: 'Create something' } });

      const generateButton = screen.getByText('Generate');
      expect(generateButton).not.toBeDisabled();
    });

    it('should call generateCode API when clicking Generate', async () => {
      api.getSession.mockResolvedValue(mockSession);
      api.generateCode = jest.fn().mockResolvedValue({
        code: 'def hello():\n    print("Hello")',
        error: '',
      });

      renderWithRouter(<SessionPage />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Ask AI to generate/i)).toBeInTheDocument();
      });

      const promptInput = screen.getByPlaceholderText(/Ask AI to generate/i);
      fireEvent.change(promptInput, { target: { value: 'Create a hello function' } });

      const generateButton = screen.getByText('Generate');
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(api.generateCode).toHaveBeenCalledWith(
          'Create a hello function',
          'print("hello")',
          'python'
        );
      });
    });

    it('should show loading state during generation', async () => {
      api.getSession.mockResolvedValue(mockSession);
      api.generateCode = jest.fn().mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve({ code: 'test', error: '' }), 100))
      );

      renderWithRouter(<SessionPage />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Ask AI to generate/i)).toBeInTheDocument();
      });

      const promptInput = screen.getByPlaceholderText(/Ask AI to generate/i);
      fireEvent.change(promptInput, { target: { value: 'Create something' } });

      const generateButton = screen.getByText('Generate');
      fireEvent.click(generateButton);

      expect(screen.getByText('Generating...')).toBeInTheDocument();
    });

    it('should display AI error message', async () => {
      api.getSession.mockResolvedValue(mockSession);
      api.generateCode = jest.fn().mockResolvedValue({
        code: '',
        error: 'AI service unavailable',
      });

      renderWithRouter(<SessionPage />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/Ask AI to generate/i)).toBeInTheDocument();
      });

      const promptInput = screen.getByPlaceholderText(/Ask AI to generate/i);
      fireEvent.change(promptInput, { target: { value: 'Create something' } });

      const generateButton = screen.getByText('Generate');
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('AI service unavailable')).toBeInTheDocument();
      });
    });
  });
});


