"""
Scheduler Module
APScheduler-based scheduled task management
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Callable, Optional


class PaperScheduler:
    """Scheduled task manager"""

    def __init__(
        self,
        daily_task_func: Callable,
        trigger_time: str = "21:00",
        timezone: str = "UTC",
    ):
        """
        Initialize scheduler

        Args:
            daily_task_func: Function to run daily
            trigger_time: Daily trigger time (HH:MM)
            timezone: Timezone for scheduling
        """
        self.daily_task_func = daily_task_func
        self.trigger_time = trigger_time
        self.timezone = timezone
        self.scheduler = BlockingScheduler()

    def start(self, run_immediately: bool = False):
        """
        Start scheduler

        Args:
            run_immediately: Run task immediately before scheduling
        """
        # Add daily job
        hour, minute = self.trigger_time.split(":")
        self.scheduler.add_job(
            self.daily_task_func,
            "cron",
            hour=int(hour),
            minute=int(minute),
            timezone=self.timezone,
            id="daily_paper_search",
            replace_existing=True,
        )

        print(f"[Scheduler] Scheduled daily task at {self.trigger_time} ({self.timezone})")

        if run_immediately:
            print("[Scheduler] Running task immediately...")
            try:
                self.daily_task_func()
            except Exception as e:
                print(f"[Scheduler] Immediate run failed: {e}")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("[Scheduler] Stopped")

    def stop(self):
        """Stop scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            print("[Scheduler] Scheduler stopped")
