import logging
import pickle
import os
from tokenbucket import TokenBucketAlgo
import redis
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
load_dotenv()
redis_client = redis.Redis(host=os.environ.get("Host", "localhost"), port=6379, db=0, password=os.environ.get("REDIS_PASSWORD", "")
)

class RateLimiter(object):

    def TokenBucket(self, ip_address):
        cached_bucket = redis_client.get(f"{ip_address}")
        if cached_bucket:
            token_obj = pickle.loads(cached_bucket)
        else:
            token_obj = TokenBucketAlgo()
            logger.info(f"New bucket created for {ip_address}")

        result = token_obj.accept_request()
        logger.info(f"IP {ip_address} | tokens remaining: {token_obj.token} | allowed: {result}")

        redis_client.setex(f"{ip_address}", 3600, pickle.dumps(token_obj))
        return result
