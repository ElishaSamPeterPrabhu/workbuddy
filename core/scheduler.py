"""
Scheduler module for WorkBuddy (Jarvis Assistant).

Handles scheduling, firing, and persistence of reminders using APScheduler.
On startup, reloads all pending reminders from storage and schedules or fires them as needed.
"""

from datetime import datetime
from typing import Any, Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from core import storage
from core.notifications import show_notification
import logging
from integrations.github import GitHubIntegration


scheduler = BackgroundScheduler()
scheduler.start()

github_integration = GitHubIntegration()

GITHUB_POLL_INTERVAL_MINUTES = 5


def _reminder_job(reminder_id: int, message: str) -> None:
    """Job to fire when a reminder is due."""
    show_notification("WorkBuddy Reminder", message)
    storage.mark_reminder_done(reminder_id)
    storage.add_notification("WorkBuddy Reminder", message)


def schedule_reminder(message: str, remind_at: datetime) -> int:
    """Add a reminder to storage and schedule it with APScheduler. Returns the reminder ID."""
    reminder_id = storage.add_reminder(message, remind_at.isoformat())
    print(f"Scheduling reminder {reminder_id} for {remind_at}")
    scheduler.add_job(
        _reminder_job,
        "date",
        run_date=remind_at,
        args=[reminder_id, message],
        id=f"reminder_{reminder_id}",
        replace_existing=True,
    )
    return reminder_id


def reload_reminders() -> None:
    """Reload all pending reminders from storage and schedule or fire them as needed."""
    now = datetime.now()
    for reminder_id, message, remind_at_str in storage.get_pending_reminders():
        try:
            remind_at = datetime.fromisoformat(remind_at_str)
        except ValueError:
            continue  # Skip invalid dates
        if remind_at <= now:
            # Missed reminder: fire immediately
            show_notification("Missed Reminder", message)
            storage.mark_reminder_done(reminder_id)
            storage.add_notification("Missed Reminder", message)
        else:
            # Schedule future reminder
            scheduler.add_job(
                _reminder_job,
                "date",
                run_date=remind_at,
                args=[reminder_id, message],
                id=f"reminder_{reminder_id}",
                replace_existing=True,
            )


def cancel_reminder(reminder_id: int) -> None:
    """Cancel a scheduled reminder by ID."""
    try:
        scheduler.remove_job(f"reminder_{reminder_id}")
    except JobLookupError:
        pass


def get_all_reminders_with_status() -> list[dict]:
    """Get all reminders with their status as a string."""
    return storage.get_all_reminders_with_status()


def reschedule_reminder(
    reminder_id: int, new_message: str, new_remind_at: datetime
) -> None:
    """Cancel and reschedule a reminder job with updated message and time."""
    cancel_reminder(reminder_id)
    logging.info(
        f"[Scheduler] Rescheduling reminder id={reminder_id} new_message={new_message} new_time={new_remind_at.isoformat()}"
    )
    scheduler.add_job(
        _reminder_job,
        "date",
        run_date=new_remind_at,
        args=[reminder_id, new_message],
        id=f"reminder_{reminder_id}",
        replace_existing=True,
    )


def poll_github() -> None:
    """Poll GitHub for new notifications and PRs, and trigger updates if found."""
    if not github_integration.is_configured():
        logging.info("[GitHub Poll] Integration not configured.")
        return
    notifications = github_integration.get_notifications()
    prs = github_integration.get_pull_requests()
    # TODO: Call notification/UI update callback here
    logging.info(
        f"[GitHub Poll] {len(notifications) if isinstance(notifications, list) else 0} notifications, {len(prs) if isinstance(prs, list) else 0} PRs."
    )


# Schedule the polling job
scheduler.add_job(
    poll_github,
    "interval",
    minutes=GITHUB_POLL_INTERVAL_MINUTES,
    id="github_polling_job",
    replace_existing=True,
)
