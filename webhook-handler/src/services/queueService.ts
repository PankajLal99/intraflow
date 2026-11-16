import Queue from 'bull';
import Redis from 'ioredis';
import { config } from '../config/config';
import { processMessage } from '../processors/messageProcessor';
import { Counter, Histogram } from 'prom-client';

let messageQueue: Queue.Queue;
let redisClient: Redis;

const queuedMessagesCounter = new Counter({
  name: 'webhook_messages_queued_total',
  help: 'Total number of messages queued'
});

const processingDuration = new Histogram({
  name: 'webhook_message_processing_duration_seconds',
  help: 'Duration of message processing',
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30]
});

const processingErrorsCounter = new Counter({
  name: 'webhook_message_processing_errors_total',
  help: 'Total number of message processing errors'
});

export async function initializeQueue() {
  redisClient = new Redis(config.redis.url);
  
  messageQueue = new Queue('whatsapp-messages', config.redis.url, {
    defaultJobOptions: {
      attempts: config.rateLimit.maxRetries,
      backoff: {
        type: 'exponential',
        delay: 2000
      },
      removeOnComplete: 100,
      removeOnFail: false
    }
  });

  messageQueue.process(async (job) => {
    const start = Date.now();
    try {
      await processMessage(job.data);
      const duration = (Date.now() - start) / 1000;
      processingDuration.observe(duration);
      return { success: true };
    } catch (error: any) {
      processingErrorsCounter.inc();
      throw error;
    }
  });

  messageQueue.on('completed', (job) => {
    console.log(`Job ${job.id} completed`);
  });

  messageQueue.on('failed', (job, err) => {
    console.error(`Job ${job.id} failed:`, err.message);
  });

  return messageQueue;
}

export async function addMessageToQueue(data: any) {
  queuedMessagesCounter.inc();
  return messageQueue.add(data, {
    priority: 1,
    jobId: data.messageId
  });
}

export async function checkRedisHealth(): Promise<boolean> {
  try {
    await redisClient.ping();
    return true;
  } catch (error) {
    return false;
  }
}

export function getQueue() {
  return messageQueue;
}
