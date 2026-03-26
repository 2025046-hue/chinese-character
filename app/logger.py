import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "tracing_results.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("TracingLogger")
