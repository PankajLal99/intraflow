import axios, { AxiosInstance } from 'axios';
import { config } from '../config/config';
import { AgentRequest, AgentResponse } from '../types';
import { logger } from '../index';

class AgentClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: config.agentOrchestrator.url,
      timeout: config.agentOrchestrator.timeout,
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }

  async processMessage(request: AgentRequest): Promise<AgentResponse> {
    try {
      logger.info('Calling agent orchestrator', {
        userId: request.userId,
        messageLength: request.message.length
      });

      const response = await this.client.post<AgentResponse>('/agent/process', request);
      
      logger.info('Agent response received', {
        userId: request.userId,
        agentType: response.data.agentType,
        intent: response.data.intent,
        confidence: response.data.confidence
      });

      return response.data;
      
    } catch (error: any) {
      logger.error('Agent orchestrator call failed', {
        error: error.message,
        userId: request.userId,
        status: error.response?.status,
        data: error.response?.data
      });

      return {
        success: false,
        response: 'I apologize, but I\'m having trouble processing your request right now. Please try again in a moment.',
        metadata: {
          error: error.message,
          fallback: true
        }
      };
    }
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

export const agentClient = new AgentClient();
