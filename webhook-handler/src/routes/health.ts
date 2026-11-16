import { Router, Request, Response } from 'express';
import { checkRedisHealth } from '../services/queueService';

const router = Router();

router.get('/', async (req: Request, res: Response) => {
  try {
    const redisHealthy = await checkRedisHealth();
    
    const health = {
      status: redisHealthy ? 'healthy' : 'degraded',
      service: 'webhook-handler',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      memory: {
        used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
        total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
      },
      checks: {
        redis: redisHealthy ? 'ok' : 'failed'
      }
    };
    
    const statusCode = health.status === 'healthy' ? 200 : 503;
    res.status(statusCode).json(health);
    
  } catch (error: any) {
    res.status(503).json({
      status: 'unhealthy',
      error: error.message
    });
  }
});

export default router;
