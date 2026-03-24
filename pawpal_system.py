from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
import uuid


# ══════════════════════════════════════════════════════════════
# TASK
# ══════════════════════════════════════════════════════════════

@dataclass
class Task:
    """
    Represents a single pet care activity.

    Attributes
    ----------
    description : Human-readable label, e.g. "Morning walk"
    due_time    : 24-hour time string "HH:MM", e.g. "08:30"
    due_date    : ISO date string "YYYY-MM-DD", e.g. "2025-06-01"
    frequency   : "once" | "daily" | "weekly"
    priority    : "low" | "medium" | "high"
    completed   : Whether the task has been marked done
    task_type   : "walk" | "feeding" | "medication" | "vet" | "general"
    task_id     : Unique identifier — auto-generated via uuid so two tasks
                  with the same description can still be told apart.
    """

    description: str
    due_time:    str
    due_date:    str
    frequency:   str  = "once"
    priority:    str  = "medium"
    completed:   bool = False
    task_type:   str  = "general"
    task_id:     str  = field(default_factory=lambda: str(uuid.uuid4()))

    def mark_complete(self) -> str:
        """Set completed = True and return a confirmation message."""
        self.completed = True
        return f"✅ '{self.description}' marked complete!"

    def reschedule(self) -> Optional["Task"]:
        """
        If this is a recurring task, build and return the next Task.
        Returns None for one-time tasks.

        Uses timedelta so month and year rollovers are handled automatically.
        Daily  → tomorrow  (current date + 1 day)
        Weekly → next week (current date + 7 days)
        """
        if self.frequency == "once":
            return None

        current   = date.fromisoformat(self.due_date)
        delta     = timedelta(days=1) if self.frequency == "daily" else timedelta(weeks=1)
        next_date = current + delta

        return Task(
            description=self.description,
            due_time=self.due_time,
            due_date=str(next_date),
            frequency=self.frequency,
            priority=self.priority,
            completed=False,
            task_type=self.task_type,
        )

    def to_dict(self) -> dict:
        """Convert to a plain dict — useful for saving and printing."""
        return {
            "description": self.description,
            "due_time":    self.due_time,
            "due_date":    self.due_date,
            "frequency":   self.frequency,
            "priority":    self.priority,
            "completed":   self.completed,
            "task_type":   self.task_type,
            "task_id":     self.task_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Recreate a Task from a plain dict."""
        return cls(
            description=data["description"],
            due_time=data["due_time"],
            due_date=data["due_date"],
            frequency=data.get("frequency", "once"),
            priority=data.get("priority",   "medium"),
            completed=data.get("completed", False),
            task_type=data.get("task_type", "general"),
            task_id=data.get("task_id",     str(uuid.uuid4())),
        )

    def emoji(self) -> str:
        """Return a task-type emoji for readable output."""
        return {
            "walk":       "🐾",
            "feeding":    "🍖",
            "medication": "💊",
            "vet":        "🏥",
            "general":    "📋",
        }.get(self.task_type, "📋")

    def priority_emoji(self) -> str:
        """Return a colour-coded circle matching the priority level."""
        return {
            "high":   "🔴",
            "medium": "🟡",
            "low":    "🟢",
        }.get(self.priority, "⚪")


# ══════════════════════════════════════════════════════════════
# PET
# ══════════════════════════════════════════════════════════════

@dataclass
class Pet:
    """
    Represents a pet and its collection of care tasks.

    field(default_factory=list) is used for tasks so each Pet instance
    gets its own fresh list — avoids the Python shared-default-list bug.
    """

    name:    str
    species: str
    breed:   str
    age:     int
    tasks:   list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a Task to this pet's schedule."""
        self.tasks.append(task)

    def remove_task(self, description: str) -> bool:
        """
        Remove the first task whose description matches (case-insensitive).
        Returns True if removed, False if not found.
        """
        for task in self.tasks:
            if task.description.lower() == description.lower():
                self.tasks.remove(task)
                return True
        return False

    def remove_task_by_id(self, task_id: str) -> bool:
        """
        Remove a task by its unique task_id.
        More reliable than description matching when two tasks share a label.
        """
        for task in self.tasks:
            if task.task_id == task_id:
                self.tasks.remove(task)
                return True
        return False

    def get_pending_tasks(self) -> list[Task]:
        """Return all tasks not yet completed."""
        return [t for t in self.tasks if not t.completed]

    def get_completed_tasks(self) -> list[Task]:
        """Return all tasks already completed."""
        return [t for t in self.tasks if t.completed]

    def task_count(self) -> int:
        """Total number of tasks — completed and pending combined."""
        return len(self.tasks)

    def species_emoji(self) -> str:
        """Return an emoji matching this pet's species."""
        return {
            "dog":    "🐶",
            "cat":    "🐱",
            "rabbit": "🐰",
            "bird":   "🐦",
            "fish":   "🐠",
        }.get(self.species.lower(), "🐾")

    def to_dict(self) -> dict:
        """Serialize to a plain dict."""
        return {
            "name":    self.name,
            "species": self.species,
            "breed":   self.breed,
            "age":     self.age,
            "tasks":   [t.to_dict() for t in self.tasks],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Recreate a Pet from a plain dict."""
        pet = cls(
            name=data["name"],
            species=data["species"],
            breed=data["breed"],
            age=data["age"],
        )
        pet.tasks = [Task.from_dict(t) for t in data.get("tasks", [])]
        return pet


# ══════════════════════════════════════════════════════════════
# OWNER
# ══════════════════════════════════════════════════════════════

class Owner:
    """
    Top-level data store.
    Holds a collection of Pet objects and provides get_all_tasks(),
    which gives the Scheduler a flat view of every task across every pet.
    """

    def __init__(self, name: str, email: str = ""):
        """Initialise an Owner with an empty pets list."""
        self.name:  str       = name
        self.email: str       = email
        self.pets:  list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a Pet to this owner's household."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> bool:
        """Remove a pet by name (case-insensitive). Returns True if removed."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                self.pets.remove(pet)
                return True
        return False

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Find and return a Pet by name, or None if not found."""
        for pet in self.pets:
            if pet.name.lower() == pet_name.lower():
                return pet
        return None

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """
        Return every task across every pet as (pet_name, Task) tuples.
        This is the single data-access point the Scheduler uses —
        keeping pet context attached to each task without coupling
        Scheduler directly to individual Pet objects.
        """
        result: list[tuple[str, Task]] = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet.name, task))
        return result

    def pet_count(self) -> int:
        """How many pets does this owner have?"""
        return len(self.pets)


# ══════════════════════════════════════════════════════════════
# SCHEDULER
# ══════════════════════════════════════════════════════════════

class Scheduler:
    """
    The algorithmic brain of PawPal+.
    Receives an Owner at construction time and will provide
    sorting, filtering, conflict detection, and smart scheduling.
    """

    def __init__(self, owner: Owner):
        """Attach this Scheduler to a specific Owner."""
        self.owner = owner