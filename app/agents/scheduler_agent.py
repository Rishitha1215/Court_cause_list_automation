"""Background scheduler for periodic cause-list processing."""
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app.agents.orchestrator_agent import OrchestratorAgent
from app.config import settings


class SchedulerAgent:
	def __init__(self):
		self.scheduler = BackgroundScheduler()
		self.scheduler.add_job(
			self._run_cycle,
			"interval",
			minutes=settings.scheduler_poll_interval_minutes,
			id="cause-list-cycle",
			replace_existing=True,
		)

	def _run_cycle(self) -> None:
		current_time = datetime.now().time()
		start_time = datetime.strptime(settings.scheduler_start_time, "%H:%M").time()
		end_time = datetime.strptime(settings.scheduler_end_time, "%H:%M").time()
		if start_time <= current_time <= end_time:
			OrchestratorAgent().run_full_cycle(triggered_by="scheduler")

	def start(self) -> None:
		if not self.scheduler.running:
			self.scheduler.start()

	def shutdown(self) -> None:
		if self.scheduler.running:
			self.scheduler.shutdown(wait=False)
