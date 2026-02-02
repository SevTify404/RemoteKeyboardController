import { useState, useRef, useCallback } from 'react';
import { type CommandKey, type WSIncomingMessage, type WSOutgoingMessage, type VerifyAuthResponse } from './types';

export const useRemote = (serverHost: string) => {
  const [isConnected, setIsConnected] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);
  const socket = useRef<WebSocket | null>(null);


  const verifyAuth = async (params: { challenge_id?: string; pin?: string }): Promise<VerifyAuthResponse> => {
    try {
      const response = await fetch(`http://${serverHost}/auth/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      return await response.json();
    } catch (err) {
      return { ok: false, result: null, error: "SERVER_UNREACHABLE" };
    }
  };

  //  Connexion WS
  const connectWS = useCallback((deviceToken: string) => {

    const url = `ws://${serverHost}/ws/control-panel?device_token=${deviceToken}`;
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      setWsError(null);
    };

    ws.onmessage = (event) => {
      const response: WSIncomingMessage = JSON.parse(event.data);
      if (response.type === "COMMAND" && !response.data.succes) {
        setWsError(response.data.error);
      }
    };

    ws.onclose = () => setIsConnected(false);
    socket.current = ws;
  }, [serverHost]);

  const sendCommand = (command: CommandKey) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      const msg: WSOutgoingMessage = {
        message_type: "command",
        payload: { command, text_to_type: null, message: null }
      };
      socket.current.send(JSON.stringify(msg));
    }
  };


  const sendTyping = (text: string) => {
    if (socket.current?.readyState === WebSocket.OPEN) {
      const msg: WSOutgoingMessage = {
        message_type: "typing",
        payload: { command: null, text_to_type: text, message: null }
      };
      socket.current.send(JSON.stringify(msg));
    }
  };

  const disconnect = () => {
    if (socket.current) {
      const msg: WSOutgoingMessage = { message_type: "disconnect", payload: null };
      socket.current.send(JSON.stringify(msg));
      socket.current.close();
    }
  };

  return { isConnected, wsError, verifyAuth, connectWS, sendCommand, sendTyping, disconnect };
};