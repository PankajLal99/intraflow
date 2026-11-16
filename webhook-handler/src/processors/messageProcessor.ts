import { agentClient } from '../services/agentClient';
import { openwaClient } from '../services/openwaClient';
import { logger } from '../index';
import { AgentRequest } from '../types';

interface MessageJob {
  userId: string;
  sessionId: string;
  message: string;
  messageId: string;
  messageType: string;
  timestamp: number;
}

export async function processMessage(job: MessageJob): Promise<void> {
  try {
    logger.info('Processing message', {
      userId: job.userId,
      messageId: job.messageId,
      sessionId: job.sessionId
    });

    const agentRequest: AgentRequest = {
      userId: job.userId,
      message: job.message,
      messageType: job.messageType,
      context: {
        sessionId: job.sessionId
      },
      metadata: {
        messageId: job.messageId,
        timestamp: job.timestamp
      }
    };

    const agentResponse = await agentClient.processMessage(agentRequest);

    if (agentResponse.success && agentResponse.response) {
      if (agentResponse.buttons && agentResponse.buttons.length > 0) {
        await openwaClient.sendButtonMessage(
          job.userId,
          agentResponse.response,
          agentResponse.buttons,
          job.sessionId
        );
      } else {
        await openwaClient.sendTextMessage(
          job.userId,
          agentResponse.response,
          job.sessionId
        );
      }

      logger.info('Message processed successfully', {
        userId: job.userId,
        messageId: job.messageId,
        agentType: agentResponse.agentType,
        intent: agentResponse.intent
      });
    } else {
      logger.warn('Agent processing failed', {
        userId: job.userId,
        messageId: job.messageId,
        response: agentResponse
      });
    }

  } catch (error: any) {
    logger.error('Error processing message', {
      error: error.message,
      stack: error.stack,
      userId: job.userId,
      messageId: job.messageId
    });

    try {
      await openwaClient.sendTextMessage(
        job.userId,
        'I apologize, but I encountered an error. Please try again.',
        job.sessionId
      );
    } catch (sendError: any) {
      logger.error('Failed to send error message', {
        error: sendError.message,
        userId: job.userId
      });
    }

    throw error;
  }
}
