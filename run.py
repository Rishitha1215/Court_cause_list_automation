"""
Single entry point: starts the FastAPI API and the background scheduler
together.

Run with:
    python run.py
"""
import uvicorn

from app.agents.scheduler_agent import SchedulerAgent
from app.main import app
from app.utils.logger import get_logger

logger = get_logger(__name__)


def main() -> None:
    scheduler = SchedulerAgent()
    scheduler.start()
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        scheduler.shutdown()


if __name__ == "__main__":
    main()