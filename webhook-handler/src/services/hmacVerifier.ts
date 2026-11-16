import crypto from 'crypto';
import { config } from '../config/config';

export function verifyHmacSignature(payload: string, signature: string | undefined): boolean {
  if (!signature) {
    return false;
  }

  const expectedSignature = crypto
    .createHmac('sha256', config.openwa.webhookSecret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

export function generateHmacSignature(payload: string): string {
  return crypto
    .createHmac('sha256', config.openwa.webhookSecret)
    .update(payload)
    .digest('hex');
}
