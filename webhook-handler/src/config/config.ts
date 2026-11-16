export const config = {
  nodeEnv: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  logLevel: process.env.LOG_LEVEL || 'info',
  
  openwa: {
    apiUrl: process.env.OPENWA_API_URL || 'http://openwa:2785/api',
    apiKey: process.env.OPENWA_API_KEY || '',
    webhookSecret: process.env.OPENWA_WEBHOOK_SECRET || 'change-this-secret-in-production'
  },
  
  agentOrchestrator: {
    url: process.env.AGENT_ORCHESTRATOR_URL || 'http://agent-orchestrator:8000',
    timeout: parseInt(process.env.AGENT_TIMEOUT || '30000', 10)
  },
  
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379'
  },
  
  database: {
    url: process.env.DATABASE_URL || 'postgresql://whatsapp:whatsapp123@localhost:5432/whatsapp'
  },
  
  rateLimit: {
    perMinute: parseInt(process.env.RATE_LIMIT_PER_MINUTE || '60', 10),
    maxRetries: parseInt(process.env.MAX_RETRIES || '3', 10)
  }
};

export function validateConfig() {
  const requiredEnvVars = [
    'OPENWA_WEBHOOK_SECRET',
    'OPENWA_API_KEY'
  ];
  
  const missing = requiredEnvVars.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
  }
}
