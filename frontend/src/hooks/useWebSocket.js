import { useEffect, useRef, useState } from 'react';

const stripTrailingSlash = (value) => (value || '').replace(/\/$/, '');
const API_URL = stripTrailingSlash(process.env.REACT_APP_API_URL);
const WS_URL = stripTrailingSlash(process.env.REACT_APP_WS_URL);

const safeUrl = (raw) => {
  if (!raw) return null;
  try {
    return new URL(raw);
  } catch (e) {
    return null;
  }
};

const resolveWsBase = () => {
  const current = new URL(window.location.href);
  const wsCustom = safeUrl(WS_URL);
  const apiCustom = safeUrl(API_URL);

  // Prefer explicit WS override when it makes sense for the current host
  if (wsCustom) {
    const protocol = ['https:', 'wss:'].includes(wsCustom.protocol) ? 'wss:' : 'ws:';
    return `${protocol}//${wsCustom.host}`;
  }

  // Next prefer API URL
  if (apiCustom) {
    const protocol = ['https:', 'wss:'].includes(apiCustom.protocol) ? 'wss:' : 'ws:';
    return `${protocol}//${apiCustom.host}`;
  }

  // Fallback to current origin
  const protocol = current.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${current.host}`;
};

const useWebSocket = (sessionCode, onMessage) => {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const messageHandlerRef = useRef(onMessage);

  // Keep latest onMessage without re-running the WS effect
  useEffect(() => {
    messageHandlerRef.current = onMessage;
  }, [onMessage]);

  useEffect(() => {
    const wsUrl = `${resolveWsBase()}/ws/${sessionCode}`;
    
    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            if (messageHandlerRef.current) {
              messageHandlerRef.current(message);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        ws.onclose = () => {
          setIsConnected(false);
          // Attempt to reconnect after 3 seconds
          if (!reconnectTimeoutRef.current) {
            reconnectTimeoutRef.current = setTimeout(() => {
              reconnectTimeoutRef.current = null;
              connect();
            }, 3000);
          }
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
        setIsConnected(false);
      }
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current && typeof wsRef.current.close === 'function') {
        wsRef.current.close();
      }
    };
  }, [sessionCode]);

  const sendMessage = (message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return { isConnected, sendMessage };
};

export default useWebSocket;

