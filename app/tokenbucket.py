import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)


class TokenBucketAlgo(object):

    def __init__(self, bucket_limit=8, refill_rate=3, interval=5):
        logger.info("Initiating Token bucket technique")
        
        self.bucket_limit = bucket_limit
        self.refill_rate = refill_rate
        self.interval = interval
        # Available tokens to consider for algorithm
        self.token = bucket_limit
        self.start_time = time.time()

    def refill(self):
        """Add tokens to the bucket based on elapsed time."""
        now = time.time()
        elapsed_time = now - self.start_time
        if elapsed_time >= self.interval:
            intervals_elapsed = int(elapsed_time / self.interval)
            tokens_to_add = self.refill_rate * intervals_elapsed
            self.token = min(self.bucket_limit, self.token + tokens_to_add)
            self.start_time += intervals_elapsed * self.interval
            logger.info(f"Refilled {tokens_to_add} tokens | current tokens: {self.token}")

    def accept_request(self, tokens=1):
        """Return True and consume a token if available, else False."""
        self.refill()
        if self.token >= tokens:
            self.token -= tokens
            return True
        return False