import { useEffect, useRef, useState, useCallback } from 'react';
import { getParticipantInfo } from '../utils/participantUtils';

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
  const [participants, setParticipants] = useState({});
  const [myInfo, setMyInfo] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const messageHandlerRef = useRef(onMessage);

  const updateParticipant = useCallback((userId, updater) => {
    setParticipants((prev) => {
      const currentParticipant = prev[userId] || { userId };
      return {
        ...prev,
        [userId]: updater(currentParticipant),
      };
    });
  }, []);

  // Keep latest onMessage without re-running the WS effect
  useEffect(() => {
    messageHandlerRef.current = onMessage;
  }, [onMessage]);

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((message) => {
    switch (message.type) {
      case 'welcome':
        setMyInfo({
          userId: message.userId,
          displayName: message.displayName,
          color: message.color,
        });
        const participantsMap = (message.participants || []).reduce((acc, participant) => {
          acc[participant.userId] = participant;
          return acc;
        }, {});
        setParticipants(participantsMap);
        break;

      case 'participant_join':
        updateParticipant(message.userId, () => ({
          userId: message.userId,
          displayName: message.displayName,
          color: message.color,
        }));
        break;

      case 'participant_leave':
        setParticipants((prev) => {
          const updated = { ...prev };
          delete updated[message.userId];
          return updated;
        });
        break;

      case 'cursor_update':
        updateParticipant(message.userId, (participant) => ({
          ...participant,
          cursor: message.position,
        }));
        break;

      case 'selection_update':
        updateParticipant(message.userId, (participant) => ({
          ...participant,
          selection: message.selection,
        }));
        break;

      default:
        // Pass other messages to the handler
        break;
    }

    // Always pass to external handler
    if (messageHandlerRef.current) {
      messageHandlerRef.current(message);
    }
  }, [updateParticipant]);

  useEffect(() => {
    const wsUrl = `${resolveWsBase()}/ws/${sessionCode}`;
    const participantInfo = getParticipantInfo();

    const connect = () => {
      try {
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          // Send join message immediately after connection
          ws.send(
            JSON.stringify({
              type: 'join',
              userId: participantInfo.userId,
              displayName: participantInfo.displayName,
            })
          );
          setIsConnected(true);
          if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
            reconnectTimeoutRef.current = null;
          }
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            handleMessage(message);
          } catch (_error) {
            // Ignore malformed payloads from the socket.
          }
        };

        ws.onerror = () => {};

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
      } catch (_error) {
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
  }, [sessionCode, handleMessage]);

  const sendMessage = useCallback((message) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    }
  }, []);

  // Send cursor position update
  const sendCursorPosition = useCallback(
    (position) => {
      sendMessage({
        type: 'cursor_position',
        position,
      });
    },
    [sendMessage]
  );

  // Send selection update
  const sendSelection = useCallback(
    (selection) => {
      sendMessage({
        type: 'selection_change',
        selection,
      });
    },
    [sendMessage]
  );

  return {
    isConnected,
    sendMessage,
    sendCursorPosition,
    sendSelection,
    participants,
    myInfo,
  };
};

export default useWebSocket;


