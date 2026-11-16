import { Router, Request, Response } from 'express';
import Joi from 'joi';
import { verifyHmacSignature } from '../services/hmacVerifier';
import { addMessageToQueue } from '../services/queueService';
import { logger } from '../index';
import { WebhookPayload } from '../types';

const router = Router();

const webhookSchema = Joi.object({
  event: Joi.string().required(),
  sessionId: Joi.string().required(),
  timestamp: Joi.number().required(),
  message: Joi.object({
    id: Joi.string().required(),
    from: Joi.string().required(),
    to: Joi.string().optional(),
    body: Joi.string().optional(),
    type: Joi.string().valid('text', 'image', 'audio', 'video', 'document', 'sticker').required(),
    timestamp: Joi.number().required(),
    mediaUrl: Joi.string().uri().optional(),
    caption: Joi.string().optional()
  }).optional(),
  status: Joi.object().optional()
});

router.post('/', async (req: Request, res: Response) => {
  try {
    const signature = req.headers['x-signature'] as string;
    const body = JSON.stringify(req.body);
    
    if (!verifyHmacSignature(body, signature)) {
      logger.warn('Invalid HMAC signature', { ip: req.ip });
      return res.status(401).json({ error: 'Invalid signature' });
    }

    const { error, value } = webhookSchema.validate(req.body);
    if (error) {
      logger.warn('Invalid webhook payload', { error: error.message });
      return res.status(400).json({ error: 'Invalid payload', details: error.message });
    }

    const payload: WebhookPayload = value;
    
    logger.info('Received webhook', {
      event: payload.event,
      sessionId: payload.sessionId,
      messageId: payload.message?.id
    });

    if (payload.event === 'message' && payload.message) {
      if (payload.message.type === 'text' && payload.message.body) {
        await addMessageToQueue({
          userId: payload.message.from,
          sessionId: payload.sessionId,
          message: payload.message.body,
          messageId: payload.message.id,
          messageType: payload.message.type,
          timestamp: payload.message.timestamp
        });
        
        logger.info('Message queued for processing', {
          userId: payload.message.from,
          messageId: payload.message.id
        });
      } else {
        logger.info('Ignoring non-text message', {
          messageType: payload.message.type,
          messageId: payload.message.id
        });
      }
    }

    res.status(200).json({ status: 'ok', received: true });
    
  } catch (error: any) {
    logger.error('Error processing webhook', {
      error: error.message,
      stack: error.stack
    });
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;
