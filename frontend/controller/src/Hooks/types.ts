export type CommandKey =
  | "UP" | "DOWN" | "LEFT" | "RIGHT" | "ENTER"
  | "MUTE" | "VOLUME_UP" | "VOLUME_DOWN"
  | "COPY" | "PASTE" | "SELECT_ALL" | "ALT_TAB"
  | "START_PRESENTATION" | "END_PRESENTATION";

// Structure de la réponse POST /auth/verify
export interface VerifyAuthResponse {
  ok: boolean;
  result: {
    device_id: string;
    device_token: string;
    session_token: string;
    session_expires_at: string;
  } | null;
  error: string | null;
}

export interface WSOutgoingMessage {
  message_type: "command" | "typing" | "disconnect";
  payload: {
    command: CommandKey | null;
    text_to_type: string | null;
    message: string | null;
  } | null;
}

export interface WSIncomingMessage {
  type: "COMMAND" | "NOTIFY";
  data: {
    succes: boolean;
    error: string | null;
    data: WSOutgoingMessage | null; // L'écho du message renvoyé par le serveur
    message?: string; // Pour les notifications
  };
}

export interface WaitingRoomMessage {
  challenge_id: string;
  pin: string;
  expires_in?: number; 
}

// messages enveloppés
export type BackendMessageType = "NEW_CHALLENGE" | "AUTHENTIFICATION_SUCCESS" | "COMMAND" | "NOTIFY";
export interface BackendWaitingMessage {
  type: "NEW_CHALLENGE" | "AUTHENTIFICATION_SUCCESS";
  data: {
    challenge_id?: string;
    pin?: string;
    expires_at?: string;
    device_token?: string; 
  };
}