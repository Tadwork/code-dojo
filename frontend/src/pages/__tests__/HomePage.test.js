import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import HomePage from '../HomePage';
import * as api from '../../services/api';

jest.mock('../../services/api');
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn((path) => path),
}));

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('HomePage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render homepage with title and subtitle', () => {
    renderWithRouter(<HomePage />);

    expect(screen.getByText('CodeDojo')).toBeInTheDocument();
    expect(
      screen.getByText('Collaborative coding interview practice platform')
    ).toBeInTheDocument();
  });

  it('should render session creation form', () => {
    renderWithRouter(<HomePage />);

    expect(screen.getByLabelText(/Session Title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Programming Language/i)).toBeInTheDocument();
    expect(screen.getByText('Create Session')).toBeInTheDocument();
  });

  it('should allow entering session title', () => {
    renderWithRouter(<HomePage />);

    const titleInput = screen.getByLabelText(/Session Title/i);
    fireEvent.change(titleInput, { target: { value: 'Interview with John' } });

    expect(titleInput.value).toBe('Interview with John');
  });

  it('should allow selecting programming language', () => {
    renderWithRouter(<HomePage />);

    const languageSelect = screen.getByLabelText(/Programming Language/i);
    fireEvent.change(languageSelect, { target: { value: 'javascript' } });

    expect(languageSelect.value).toBe('javascript');
  });

  it('should create session on form submit', async () => {
    const mockSession = {
      id: 'test-id',
      session_code: 'TEST1234',
      title: 'Test Session',
      language: 'python',
    };

    api.createSession.mockResolvedValue(mockSession);

    renderWithRouter(<HomePage />);

    const titleInput = screen.getByLabelText(/Session Title/i);
    fireEvent.change(titleInput, { target: { value: 'Test Session' } });

    const submitButton = screen.getByText('Create Session');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(api.createSession).toHaveBeenCalledWith('Test Session', 'python');
    });
  });

  it('should show loading state while creating session', async () => {
    api.createSession.mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 100))
    );

    renderWithRouter(<HomePage />);

    const submitButton = screen.getByText('Create Session');
    fireEvent.click(submitButton);

    expect(screen.getByText('Creating...')).toBeInTheDocument();
    expect(screen.getByText('Creating...')).toBeDisabled();
  });

  it('should display error message on session creation failure', async () => {
    const error = {
      response: {
        data: {
          detail: 'Failed to create session',
        },
      },
    };

    api.createSession.mockRejectedValue(error);

    renderWithRouter(<HomePage />);

    const submitButton = screen.getByText('Create Session');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Failed to create session')).toBeInTheDocument();
    });
  });

  it('should display "How it works" section', () => {
    renderWithRouter(<HomePage />);

    expect(screen.getByText('How it works:')).toBeInTheDocument();
    expect(screen.getByText('Create a new session')).toBeInTheDocument();
    expect(screen.getByText('Share the link with candidates')).toBeInTheDocument();
    expect(screen.getByText('Code together in real-time')).toBeInTheDocument();
    expect(
      screen.getByText('Execute code safely in the browser')
    ).toBeInTheDocument();
  });
});

