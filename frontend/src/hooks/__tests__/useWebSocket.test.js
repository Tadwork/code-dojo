import { act, renderHook, waitFor } from '@testing-library/react';
import useWebSocket from '../useWebSocket';

// Mock participantUtils
jest.mock('../../utils/participantUtils', () => ({
  getParticipantInfo: () => ({
    userId: 'test-user-123',
    displayName: 'Test User',
  }),
  hexToRgba: (hex, alpha) => `rgba(0, 0, 0, ${alpha})`,
}));

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = MockWebSocket.CONNECTING;
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.onclose = null;
    this.sentMessages = [];
    mockWebSocketInstances.push(this);
  }

  send(data) {
    this.sentMessages.push(JSON.parse(data));
  }

  close() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose();
    }
  }

  // Helper methods for testing
  simulateOpen() {
    this.readyState = MockWebSocket.OPEN;
    if (this.onopen) {
      this.onopen();
    }
  }

  simulateMessage(data) {
    if (this.onmessage) {
      this.onmessage({ data: JSON.stringify(data) });
    }
  }

  simulateError() {
    if (this.onerror) {
      this.onerror(new Error('WebSocket error'));
    }
  }

  simulateClose() {
    this.readyState = MockWebSocket.CLOSED;
    if (this.onclose) {
      this.onclose();
    }
  }
}

MockWebSocket.CONNECTING = 0;
MockWebSocket.OPEN = 1;
MockWebSocket.CLOSING = 2;
MockWebSocket.CLOSED = 3;

// Mock WebSocket globally
const mockWebSocketInstances = [];

global.WebSocket = jest.fn((url) => new MockWebSocket(url));
global.window.WebSocket = global.WebSocket;

// Set static properties
Object.assign(global.WebSocket, {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
});

describe('useWebSocket', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockWebSocketInstances.length = 0;
    global.WebSocket.mockImplementation((url) => new MockWebSocket(url));

    Object.defineProperty(window, 'location', {
      value: {
        href: 'http://localhost:3000',
        protocol: 'http:',
        host: 'localhost:3000',
      },
      writable: true,
    });
  });

  it('should initialize WebSocket connection', () => {
    const onMessage = jest.fn();
    renderHook(() => useWebSocket('TEST1234', onMessage));

    expect(global.WebSocket).toHaveBeenCalled();
  });

  it('should send join message on connection open', async () => {
    const onMessage = jest.fn();
    renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());

    expect(ws.sentMessages).toHaveLength(1);
    expect(ws.sentMessages[0]).toEqual({
      type: 'join',
      userId: 'test-user-123',
      displayName: 'Test User',
    });
  });

  it('should set connected state when WebSocket opens', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });
  });

  it('should handle welcome message and set myInfo', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());
    act(() =>
      ws.simulateMessage({
        type: 'welcome',
        userId: 'test-user-123',
        displayName: 'Test User',
        color: '#FF6B6B',
        code: 'print("hello")',
        language: 'python',
        participants: [],
      })
    );

    await waitFor(() => {
      expect(result.current.myInfo).toEqual({
        userId: 'test-user-123',
        displayName: 'Test User',
        color: '#FF6B6B',
      });
    });
  });

  it('should track participants from welcome message', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());
    act(() =>
      ws.simulateMessage({
        type: 'welcome',
        userId: 'test-user-123',
        displayName: 'Test User',
        color: '#FF6B6B',
        participants: [
          { userId: 'other-user', displayName: 'Other User', color: '#4ECDC4' },
        ],
      })
    );

    await waitFor(() => {
      expect(Object.keys(result.current.participants)).toHaveLength(1);
    });
    expect(result.current.participants['other-user'].displayName).toBe(
      'Other User'
    );
  });

  it('should handle participant_join', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());
    act(() =>
      ws.simulateMessage({
        type: 'participant_join',
        userId: 'new-user',
        displayName: 'New User',
        color: '#45B7D1',
      })
    );

    await waitFor(() => {
      expect(result.current.participants['new-user']).toBeDefined();
    });
    expect(result.current.participants['new-user'].displayName).toBe(
      'New User'
    );
  });

  it('should handle participant_leave', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());
    act(() =>
      ws.simulateMessage({
        type: 'welcome',
        userId: 'test-user-123',
        displayName: 'Test User',
        color: '#FF6B6B',
        participants: [
          { userId: 'other-user', displayName: 'Other User', color: '#4ECDC4' },
        ],
      })
    );

    await waitFor(() => {
      expect(result.current.participants['other-user']).toBeDefined();
    });

    act(() =>
      ws.simulateMessage({
        type: 'participant_leave',
        userId: 'other-user',
      })
    );

    await waitFor(() => {
      expect(result.current.participants['other-user']).toBeUndefined();
    });
  });

  it('should handle cursor_update', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());
    act(() =>
      ws.simulateMessage({
        type: 'welcome',
        userId: 'test-user-123',
        displayName: 'Test User',
        color: '#FF6B6B',
        participants: [
          { userId: 'other-user', displayName: 'Other User', color: '#4ECDC4' },
        ],
      })
    );

    await waitFor(() => {
      expect(result.current.participants['other-user']).toBeDefined();
    });

    act(() =>
      ws.simulateMessage({
        type: 'cursor_update',
        userId: 'other-user',
        position: { lineNumber: 5, column: 10 },
      })
    );

    await waitFor(() => {
      expect(result.current.participants['other-user'].cursor).toEqual({
        lineNumber: 5,
        column: 10,
      });
    });
  });

  it('should send cursor position updates', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    act(() => {
      result.current.sendCursorPosition({ lineNumber: 3, column: 5 });
    });

    expect(ws.sentMessages).toContainEqual({
      type: 'cursor_position',
      position: { lineNumber: 3, column: 5 },
    });
  });

  it('should send selection updates', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
    });

    act(() => {
      result.current.sendSelection({
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: 2,
        endColumn: 5,
      });
    });

    expect(ws.sentMessages).toContainEqual({
      type: 'selection_change',
      selection: {
        startLineNumber: 1,
        startColumn: 1,
        endLineNumber: 2,
        endColumn: 5,
      },
    });
  });

  it('should call onMessage when receiving messages', async () => {
    const onMessage = jest.fn();
    renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());
    act(() => ws.simulateMessage({ type: 'code_update', code: 'test code' }));

    await waitFor(() => {
      expect(onMessage).toHaveBeenCalledWith({
        type: 'code_update',
        code: 'test code',
      });
    });
  });

  it('should handle WebSocket errors gracefully', async () => {
    const onMessage = jest.fn();
    const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

    renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    act(() => mockWebSocketInstances[0].simulateError());

    expect(consoleErrorSpy).toHaveBeenCalled();
    consoleErrorSpy.mockRestore();
  });

  it('should cleanup WebSocket on unmount', async () => {
    const onMessage = jest.fn();
    const { unmount } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());

    unmount();

    expect(ws.readyState).toBe(MockWebSocket.CLOSED);
  });
});
