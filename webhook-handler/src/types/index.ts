export interface WebhookPayload {
  event: string;
  sessionId: string;
  timestamp: number;
  message?: WhatsAppMessage;
  status?: StatusUpdate;
}

export interface WhatsAppMessage {
  id: string;
  from: string;
  to?: string;
  body?: string;
  type: 'text' | 'image' | 'audio' | 'video' | 'document' | 'sticker';
  timestamp: number;
  mediaUrl?: string;
  caption?: string;
  quotedMessage?: any;
}

export interface StatusUpdate {
  type: 'session' | 'message';
  status: string;
  details?: any;
}

export interface AgentRequest {
  userId: string;
  message: string;
  messageType: string;
  context?: ConversationContext;
  metadata?: Record<string, any>;
}

export interface AgentResponse {
  success: boolean;
  response: string;
  buttons?: Button[];
  nextAction?: string;
  agentType?: string;
  intent?: string;
  confidence?: number;
  metadata?: Record<string, any>;
}

export interface ConversationContext {
  conversationId?: number;
  sessionId: string;
  lastIntent?: string;
  lastAgentType?: string;
  history?: MessageHistory[];
}

export interface MessageHistory {
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface Button {
  id: string;
  text: string;
  action?: string;
}

export interface OpenWASendMessageRequest {
  sessionId: string;
  chatId: string;
  text: string;
  buttons?: any[];
}
