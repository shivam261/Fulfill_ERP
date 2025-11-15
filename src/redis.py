import redis.asyncio as aioredis
import os
from typing import Optional

JTI_EXPIRY_SECONDS = 3600  # 1 hour
token_blocklist=aioredis.from_url(url=os.getenv("REDIS_URL"))

#jti to blocklist 
