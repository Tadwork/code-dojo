import { act, renderHook, waitFor } from '@testing-library/react';
import useWebSocket from '../useWebSocket';

// Mock WebSocket
class MockWebSocket {
  constructor(url) {
    this.url = url;
    this.readyState = MockWebSocket.CONNECTING;
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.onclose = null;
    this.sentData = undefined;
    mockWebSocketInstances.push(this);
  }

  send(data) {
    this.sentData = data;
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

  it('should set connected state when WebSocket opens', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    // Wait for WebSocket to be created
    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    act(() => ws.simulateOpen());

    await waitFor(() => {
      expect(result.current.isConnected).toBe(true);
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

  it('should send messages when WebSocket is open', async () => {
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

    result.current.sendMessage({ type: 'test', data: 'hello' });

    expect(ws.sentData).toBe(JSON.stringify({ type: 'test', data: 'hello' }));
  });

  it('should not send messages when WebSocket is not open', async () => {
    const onMessage = jest.fn();
    const { result } = renderHook(() => useWebSocket('TEST1234', onMessage));

    await waitFor(() => {
      expect(mockWebSocketInstances.length).toBeGreaterThan(0);
    });

    const ws = mockWebSocketInstances[0];
    // Don't open the connection

    result.current.sendMessage({ type: 'test', data: 'hello' });

    expect(ws.sentData).toBeUndefined();
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
