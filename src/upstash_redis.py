import os
from upstash_redis import Redis
from typing import Optional
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class UpstashRedisConfig:
    def __init__(self):
        self.redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        self.redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        if not self.redis_url or not self.redis_token:
            raise ValueError("UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN must be set")

# Global Redis client
redis_client: Optional[Redis] = None

def get_upstash_redis() -> Redis:
    """Get Upstash Redis client instance"""
    global redis_client
    
    if redis_client is None:
        config = UpstashRedisConfig()
        redis_client = Redis(url=config.redis_url, token=config.redis_token)
        logger.info("✅ Upstash Redis client initialized")
    
    return redis_client

def init_upstash_redis() -> Redis:
    """Initialize and test Upstash Redis connection"""
    try:
        client = get_upstash_redis()
        # Test the connection
        test_result = client.ping()
        if test_result:
            logger.info("✅ Upstash Redis connection established successfully")
        return client
    except Exception as e:
        logger.error(f"❌ Upstash Redis connection failed: {e}")
        raise

# FastAPI dependency
def get_redis_dependency() -> Redis:
    """FastAPI dependency to get Upstash Redis client"""
    return get_upstash_redis()