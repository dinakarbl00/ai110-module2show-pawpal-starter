from dataclasses import dataclass, field
from typing import Optional
import uuid


# ══════════════════════════════════════════════════════════════
# TASK
# Represents a single pet care activity
# ══════════════════════════════════════════════════════════════

@dataclass
class Task:
    """A single pet care activity such as a walk, feeding, or medication."""

    description: str         # e.g. "Morning walk"
    due_time:    str         # e.g. "08:30"  (HH:MM, 24-hour format)
    due_date:    str         # e.g. "2025-06-01"  (YYYY-MM-DD)
    frequency:   str = "once"     # "once", "daily", or "weekly"
    priority:    str = "medium"   # "low", "medium", or "high"
    completed:   bool = False     # Has this been done yet?
    task_type:   str = "general"  # "walk", "feeding", "medication", "vet", "general"
    task_id:     str = field(default_factory=lambda: str(uuid.uuid4()))
    # task_id added so two tasks with the same description can still be told apart

    def mark_complete(self) -> str:
        """Mark this task as done. Returns a confirmation message."""
        pass

    def reschedule(self) -> Optional["Task"]:
        """If recurring, return a new Task for the next occurrence. Otherwise None."""
        pass

    def to_dict(self) -> dict:
        """Convert to a plain dict."""
        pass

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Recreate a Task from a plain dict."""
        pass

    def emoji(self) -> str:
        """Return an emoji matching the task type."""
        pass

    def priority_emoji(self) -> str:
        """Return a coloured circle matching the priority level."""
        pass


# ══════════════════════════════════════════════════════════════
# PET
# Represents a pet and its list of care tasks
# ══════════════════════════════════════════════════════════════

@dataclass
class Pet:
    """A pet with identifying info and a collection of Tasks."""

    name:    str
    species: str   # "dog", "cat", "rabbit", etc.
    breed:   str
    age:     int
    tasks:   list = field(default_factory=list)
    # default_factory=list gives each Pet its own fresh list

    def add_task(self, task: Task) -> None:
        """Add a Task to this pet's schedule."""
        pass

    def remove_task(self, description: str) -> bool:
        """Remove a task by description. Returns True if found and removed."""
        pass

    def remove_task_by_id(self, task_id: str) -> bool:
        """Remove a task by its unique task_id. More reliable when descriptions repeat."""
        pass

    def get_pending_tasks(self) -> list:
        """Return only tasks not yet completed."""
        pass

    def get_completed_tasks(self) -> list:
        """Return only completed tasks."""
        pass

    def task_count(self) -> int:
        """Return total number of tasks."""
        pass

    def species_emoji(self) -> str:
        """Return an emoji for this species."""
        pass

    def to_dict(self) -> dict:
        """Convert to a plain dict."""
        pass

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Recreate a Pet from a plain dict."""
        pass


# ══════════════════════════════════════════════════════════════
# OWNER
# Manages one or more pets; top-level data store
# ══════════════════════════════════════════════════════════════

class Owner:
    """A pet owner who manages one or more Pets."""

    def __init__(self, name: str, email: str = ""):
        """Create an Owner with an empty pets list."""
        self.name:  str  = name
        self.email: str  = email
        self.pets:  list = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's household."""
        pass

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name. Returns True if found."""
        pass

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Find and return a Pet by name, or None if not found."""
        pass

    def get_all_tasks(self) -> list:
        """
        Return all tasks across all pets as (pet_name, Task) tuples.
        This is how the Scheduler sees every task at once.
        """
        pass

    def pet_count(self) -> int:
        """Return the number of pets this owner has."""
        pass


# ══════════════════════════════════════════════════════════════
# SCHEDULER
# The "brain" — retrieves, sorts, filters, and manages tasks
# ══════════════════════════════════════════════════════════════

class Scheduler:
    """
    Algorithmic layer for PawPal+.
    Reads from Owner and operates on tasks.
    Does not store data itself.
    """

    def __init__(self, owner: Owner):
        """Attach this Scheduler to a specific Owner."""
        self.owner = owner

    def sort_by_time(self, tasks: list = None) -> list:
        """Sort tasks chronologically by due_time."""
        pass

    def sort_by_priority(self, tasks: list = None) -> list:
        """Sort tasks high → medium → low, then by time within each tier."""
        pass

    def sort_by_priority_then_time(self, tasks: list = None) -> list:
        """Sort by priority first, then time as a tiebreaker."""
        pass

    def filter_by_pet(self, pet_name: str) -> list:
        """Return only tasks for the named pet."""
        pass

    def filter_by_status(self, completed: bool) -> list:
        """Return only completed or only pending tasks."""
        pass

    def filter_by_date(self, target_date: str) -> list:
        """Return tasks due on a specific date."""
        pass

    def filter_by_priority(self, priority: str) -> list:
        """Return tasks of a specific priority level."""
        pass

    def get_todays_tasks(self) -> list:
        """Return today's tasks sorted by priority then time."""
        pass

    def detect_conflicts(self) -> list:
        """
        Check for two tasks at the same date and time.
        Returns warning strings — does not crash.
        """
        pass

    def mark_task_complete_and_reschedule(
        self, pet_name: str, task_description: str
    ) -> str:
        """Mark a task done. If recurring, add the next occurrence automatically."""
        pass

    def find_next_available_slot(
        self, target_date: str, start_time: str = "07:00"
    ) -> str:
        """Find the first free 30-minute slot on a given date."""
        pass

    def build_priority_schedule(
        self, target_date: str, max_tasks: int = 10
    ) -> list:
        """Return top-ranked pending tasks using a weighted priority score."""
        pass

    def get_summary(self) -> dict:
        """Return a metrics dict: total, completed, pending, high-priority, pets."""
        pass