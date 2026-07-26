from functools import lru_cache
import logging
import typer
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

class AlgoSettings():
    algoritm_dict = { 1: "TokenBucket", 2: "LeakyBucket" }

    def get_rate_limiter_choice(self) -> int:
        """Prompt user to select rate limiting algorithm."""
        choice = typer.prompt(
            "Select rate limiting algorithm:\n"
            "  [1] Token Bucket (default)\n"
            "  [2] Leaky Bucket\n"
            "Enter choice",
            type=int,
            default=1
        )
        if choice not in [1, 2]:
            logger.warning(f"Invalid choice {choice}, defaulting to Token Bucket")
            return 1
        return self.algoritm_dict[choice]

@lru_cache
def get_settings():
    return AlgoSettings()