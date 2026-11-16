import { Router, Request, Response } from 'express';
import { register } from 'prom-client';

const router = Router();

router.get('/', async (req: Request, res: Response) => {
  try {
    res.set('Content-Type', register.contentType);
    res.end(await register.metrics());
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
