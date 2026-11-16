import axios, { AxiosInstance } from 'axios';
import { config } from '../config/config';
import { OpenWASendMessageRequest } from '../types';
import { logger } from '../index';

class OpenWAClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: config.openwa.apiUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': config.openwa.apiKey
      }
    });
  }

  async sendTextMessage(chatId: string, text: string, sessionId: string = 'main-session'): Promise<any> {
    try {
      logger.info('Sending message via OpenWA', {
        chatId,
        sessionId,
        messageLength: text.length
      });

      const request: OpenWASendMessageRequest = {
        sessionId,
        chatId,
        text
      };

      const response = await this.client.post('/messages/text', request);
      
      logger.info('Message sent successfully', {
        chatId,
        messageId: response.data?.messageId
      });

      return response.data;
      
    } catch (error: any) {
      logger.error('Failed to send message via OpenWA', {
        error: error.message,
        chatId,
        status: error.response?.status,
        data: error.response?.data
      });
      throw error;
    }
  }

  async sendButtonMessage(
    chatId: string,
    text: string,
    buttons: any[],
    sessionId: string = 'main-session'
  ): Promise<any> {
    try {
      const response = await this.client.post('/messages/buttons', {
        sessionId,
        chatId,
        text,
        buttons
      });

      return response.data;
    } catch (error: any) {
      logger.error('Failed to send button message', {
        error: error.message,
        chatId
      });
      throw error;
    }
  }

  async getSessionStatus(sessionId: string = 'main-session'): Promise<any> {
    try {
      const response = await this.client.get(`/sessions/${sessionId}`);
      return response.data;
    } catch (error: any) {
      logger.error('Failed to get session status', {
        error: error.message,
        sessionId
      });
      throw error;
    }
  }
}

export const openwaClient = new OpenWAClient();
