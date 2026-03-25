import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ══════════════════════════════════════════════════════════════
# FIXTURES
# ══════════════════════════════════════════════════════════════

@pytest.fixture
def today() -> str:
    return str(date.today())

@pytest.fixture
def tomorrow() -> str:
    return str(date.today() + timedelta(days=1))

@pytest.fixture
def next_week() -> str:
    return str(date.today() + timedelta(weeks=1))

@pytest.fixture
def sample_task(today) -> Task:
    return Task(
        description="Morning walk",
        due_time="08:00",
        due_date=today,
        frequency="daily",
        priority="high",
        task_type="walk",
    )

@pytest.fixture
def sample_pet(sample_task) -> Pet:
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
    pet.add_task(sample_task)
    return pet

@pytest.fixture
def sample_owner(sample_pet) -> Owner:
    owner = Owner(name="Alex", email="alex@test.com")
    owner.add_pet(sample_pet)
    return owner

@pytest.fixture
def scheduler(sample_owner) -> Scheduler:
    return Scheduler(sample_owner)


# ══════════════════════════════════════════════════════════════
# BLOCK 1 — Task completion
# These two tests were written in the previous step and are kept here.
# ══════════════════════════════════════════════════════════════

def test_mark_complete_changes_status(sample_task):
    """mark_complete() must flip completed from False to True."""
    assert sample_task.completed is False
    sample_task.mark_complete()
    assert sample_task.completed is True

def test_mark_complete_returns_message(sample_task):
    """mark_complete() should return a non-empty confirmation string."""
    result = sample_task.mark_complete()
    assert isinstance(result, str)
    assert len(result) > 0


# ══════════════════════════════════════════════════════════════
# BLOCK 2 — Adding tasks to a Pet
# These two tests were written in the previous step and are kept here.
# ══════════════════════════════════════════════════════════════

def test_add_task_increases_count(today):
    """Each add_task() call should increase task_count() by 1."""
    pet = Pet(name="Luna", species="cat", breed="Persian", age=2)
    assert pet.task_count() == 0

    pet.add_task(Task("Feeding", "08:00", today, "daily", "high", task_type="feeding"))
    assert pet.task_count() == 1

    pet.add_task(Task("Playtime", "15:00", today, "daily", "low", task_type="general"))
    assert pet.task_count() == 2

def test_pet_tracks_pending_and_completed(today):
    """After marking one task done, pending and completed counts should update."""
    pet = Pet(name="Rex", species="dog", breed="Poodle", age=4)
    pet.add_task(Task("Walk", "08:00", today, "daily", "high", task_type="walk"))
    pet.add_task(Task("Feed", "09:00", today, "daily", "high", task_type="feeding"))

    assert len(pet.get_pending_tasks())   == 2
    assert len(pet.get_completed_tasks()) == 0

    pet.tasks[0].mark_complete()

    assert len(pet.get_pending_tasks())   == 1
    assert len(pet.get_completed_tasks()) == 1


# ══════════════════════════════════════════════════════════════
# BLOCK 3 — Sorting correctness
# ══════════════════════════════════════════════════════════════

def test_sort_by_time_is_chronological(today):
    """sort_by_time() must return tasks from earliest to latest."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=1)
    # add tasks out of order deliberately
    pet.add_task(Task("Afternoon walk", "14:00", today, "once", "low",    task_type="walk"))
    pet.add_task(Task("Morning meds",   "08:00", today, "once", "high",   task_type="medication"))
    pet.add_task(Task("Noon feeding",   "12:00", today, "once", "medium", task_type="feeding"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    times = [task.due_time for _, task in sched.sort_by_time()]
    assert times == sorted(times)

def test_sort_by_priority_high_first(today):
    """sort_by_priority() must put high-priority tasks before low ones."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Cat", species="cat", breed="Any", age=1)
    pet.add_task(Task("Low task",    "09:00", today, "once", "low"))
    pet.add_task(Task("High task",   "10:00", today, "once", "high"))
    pet.add_task(Task("Medium task", "08:00", today, "once", "medium"))
    owner.add_pet(pet)

    sched      = Scheduler(owner)
    priorities = [task.priority for _, task in sched.sort_by_priority()]
    assert priorities[0]  == "high"
    assert priorities[-1] == "low"

def test_sort_by_priority_tiebreak_by_time(today):
    """Two tasks with the same priority should be sub-sorted by time."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=1)
    pet.add_task(Task("High late",  "14:00", today, "once", "high"))
    pet.add_task(Task("High early", "07:00", today, "once", "high"))
    owner.add_pet(pet)

    sched  = Scheduler(owner)
    result = sched.sort_by_priority_then_time()
    assert result[0][1].due_time == "07:00"


# ══════════════════════════════════════════════════════════════
# BLOCK 4 — Recurring task rescheduling
# ══════════════════════════════════════════════════════════════

def test_daily_task_reschedules_to_tomorrow(today, tomorrow):
    """Completing a daily task must add a new task for tomorrow."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=2)
    pet.add_task(Task("Daily walk", "07:00", today, "daily", "high", task_type="walk"))
    owner.add_pet(pet)
    sched = Scheduler(owner)

    before = pet.task_count()
    sched.mark_task_complete_and_reschedule("Dog", "Daily walk")

    assert pet.task_count()        == before + 1   # one new task added
    assert pet.tasks[-1].due_date  == tomorrow      # it is for tomorrow
    assert pet.tasks[-1].completed is False          # it starts incomplete

def test_weekly_task_reschedules_to_next_week(today, next_week):
    """Completing a weekly task must add a new task 7 days later."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Rabbit", species="rabbit", breed="Any", age=1)
    pet.add_task(Task("Cage clean", "10:00", today, "weekly", "medium"))
    owner.add_pet(pet)
    sched = Scheduler(owner)

    sched.mark_task_complete_and_reschedule("Rabbit", "Cage clean")
    assert pet.tasks[-1].due_date == next_week

def test_once_task_does_not_reschedule(today):
    """A one-time task must NOT create a follow-up after completion."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Cat", species="cat", breed="Any", age=3)
    pet.add_task(Task("Vet visit", "10:00", today, "once", "high", task_type="vet"))
    owner.add_pet(pet)
    sched = Scheduler(owner)

    before = pet.task_count()
    sched.mark_task_complete_and_reschedule("Cat", "Vet visit")
    assert pet.task_count() == before   # no new task created

def test_completing_unknown_task_returns_error(scheduler):
    """Trying to complete a task that does not exist should return an error string."""
    result = scheduler.mark_task_complete_and_reschedule("Buddy", "Does not exist")
    assert "❌" in result


# ══════════════════════════════════════════════════════════════
# BLOCK 5 — Conflict detection
# ══════════════════════════════════════════════════════════════

def test_conflict_detected_for_same_slot(today):
    """Two tasks at the same date and time should produce a conflict warning."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=2)
    pet.add_task(Task("Walk",     "09:00", today, "once", "high", task_type="walk"))
    pet.add_task(Task("Vet",      "09:00", today, "once", "high", task_type="vet"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    assert len(sched.detect_conflicts()) > 0

def test_no_conflict_for_different_times(today):
    """Tasks at different times must not produce any warnings."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=2)
    pet.add_task(Task("Walk", "07:00", today, "once", "high"))
    pet.add_task(Task("Vet",  "10:00", today, "once", "high"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    assert sched.detect_conflicts() == []

def test_no_conflict_same_time_different_dates(today, tomorrow):
    """Same time but different dates must not be flagged as a conflict."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Cat", species="cat", breed="Any", age=1)
    pet.add_task(Task("Feed", "08:00", today,    "once", "high"))
    pet.add_task(Task("Feed", "08:00", tomorrow, "once", "high"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    assert sched.detect_conflicts() == []


# ══════════════════════════════════════════════════════════════
# BLOCK 6 — Filtering
# ══════════════════════════════════════════════════════════════

def test_filter_by_pet_returns_correct_subset(today):
    """filter_by_pet() must only return tasks for the named pet."""
    owner = Owner(name="Tester")
    dog   = Pet(name="Fido", species="dog", breed="Any", age=2)
    cat   = Pet(name="Luna", species="cat", breed="Any", age=3)
    dog.add_task(Task("Dog walk",    "08:00", today, "daily", "high", task_type="walk"))
    cat.add_task(Task("Cat feeding", "09:00", today, "daily", "high", task_type="feeding"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    sched     = Scheduler(owner)
    dog_tasks = sched.filter_by_pet("Fido")
    assert len(dog_tasks)       == 1
    assert dog_tasks[0][0]      == "Fido"

def test_filter_by_status_pending_only(today):
    """filter_by_status(False) must return only incomplete tasks."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=1)
    done  = Task("Done task",    "08:00", today, "once", "low")
    done.completed = True
    pend  = Task("Pending task", "09:00", today, "once", "high")
    pet.add_task(done)
    pet.add_task(pend)
    owner.add_pet(pet)

    sched   = Scheduler(owner)
    pending = sched.filter_by_status(completed=False)
    assert len(pending)                == 1
    assert pending[0][1].description   == "Pending task"

def test_filter_by_priority_returns_correct_level(today):
    """filter_by_priority('high') must return only high-priority tasks."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=1)
    pet.add_task(Task("High task",   "08:00", today, "once", "high"))
    pet.add_task(Task("Low task",    "09:00", today, "once", "low"))
    pet.add_task(Task("Medium task", "10:00", today, "once", "medium"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    highs = sched.filter_by_priority("high")
    assert len(highs)              == 1
    assert highs[0][1].priority    == "high"


# ══════════════════════════════════════════════════════════════
# BLOCK 7 — Edge cases
# ══════════════════════════════════════════════════════════════

def test_pet_with_no_tasks_does_not_crash():
    """A pet with zero tasks should not crash any method."""
    pet = Pet(name="Empty", species="cat", breed="Any", age=1)
    assert pet.task_count()          == 0
    assert pet.get_pending_tasks()   == []
    assert pet.get_completed_tasks() == []

def test_owner_with_no_pets_does_not_crash():
    """An owner with no pets should return empty results without crashing."""
    owner = Owner(name="Petless")
    sched = Scheduler(owner)
    assert sched.sort_by_time()     == []
    assert sched.detect_conflicts() == []
    assert sched.get_todays_tasks() == []

def test_find_next_slot_skips_booked_times(today):
    """find_next_available_slot should skip 07:00 and 07:30 and return 08:00."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=2)
    pet.add_task(Task("A", "07:00", today, "once", "low"))
    pet.add_task(Task("B", "07:30", today, "once", "low"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    assert sched.find_next_available_slot(today, "07:00") == "08:00"

def test_find_next_slot_returns_start_when_nothing_booked(tomorrow):
    """When no tasks exist the first slot should equal the start_time itself."""
    owner = Owner(name="Tester")
    sched = Scheduler(owner)
    assert sched.find_next_available_slot(tomorrow, "09:00") == "09:00"

def test_remove_nonexistent_pet_returns_false(sample_owner):
    """Removing a pet that does not exist should return False, not crash."""
    assert sample_owner.remove_pet("GhostPet") is False

def test_get_pet_returns_none_when_missing(sample_owner):
    """get_pet() for an unknown name should return None."""
    assert sample_owner.get_pet("NoSuchPet") is None


# ══════════════════════════════════════════════════════════════
# BLOCK 8 — JSON persistence
# ══════════════════════════════════════════════════════════════

def test_save_and_load_preserves_all_data(tmp_path, today):
    """Round-tripping through JSON must preserve owner, pet, and task data."""
    owner = Owner(name="JSON Tester", email="json@test.com")
    pet   = Pet(name="JsonDog", species="dog", breed="Poodle", age=2)
    pet.add_task(Task(
        description="Saved task",
        due_time="10:00",
        due_date=today,
        frequency="daily",
        priority="medium",
        task_type="walk",
    ))
    owner.add_pet(pet)

    filepath = str(tmp_path / "test_data.json")
    owner.save_to_json(filepath)
    loaded = Owner.load_from_json(filepath)

    assert loaded is not None
    assert loaded.name                          == "JSON Tester"
    assert loaded.email                         == "json@test.com"
    assert len(loaded.pets)                     == 1
    assert loaded.pets[0].name                  == "JsonDog"
    assert loaded.pets[0].task_count()          == 1
    assert loaded.pets[0].tasks[0].description  == "Saved task"
    assert loaded.pets[0].tasks[0].frequency    == "daily"

def test_load_returns_none_for_missing_file(tmp_path):
    """load_from_json should return None, not crash, when file does not exist."""
    result = Owner.load_from_json(str(tmp_path / "nonexistent.json"))
    assert result is None

def test_completed_status_survives_json_round_trip(tmp_path, today):
    """A completed task should still be completed after save and reload."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=1)
    task  = Task("Walk", "08:00", today, "once", "high")
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)

    fp = str(tmp_path / "round_trip.json")
    owner.save_to_json(fp)
    loaded = Owner.load_from_json(fp)

    assert loaded.pets[0].tasks[0].completed is True


# ══════════════════════════════════════════════════════════════
# BLOCK 9 — Priority-weighted schedule
# ══════════════════════════════════════════════════════════════

def test_high_priority_ranked_first_in_schedule(today):
    """build_priority_schedule() must put high-priority tasks before low ones."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=1)
    pet.add_task(Task("Low task",  "08:00", today, "once", "low"))
    pet.add_task(Task("High task", "09:00", today, "once", "high"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    plan  = sched.build_priority_schedule(today, max_tasks=5)
    assert plan[0][1].priority == "high"

def test_medication_bonus_beats_same_priority(today):
    """A medium medication task should outscore a medium general task."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Cat", species="cat", breed="Any", age=2)
    pet.add_task(Task("General medium", "08:00", today, "once", "medium", task_type="general"))
    pet.add_task(Task("Med medium",     "09:00", today, "once", "medium", task_type="medication"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    plan  = sched.build_priority_schedule(today, max_tasks=5)
    assert plan[0][1].task_type == "medication"

def test_max_tasks_limits_output(today):
    """build_priority_schedule(max_tasks=2) should return at most 2 tasks."""
    owner = Owner(name="Tester")
    pet   = Pet(name="Dog", species="dog", breed="Any", age=1)
    for i in range(6):
        pet.add_task(Task(f"Task {i}", f"0{i+7}:00", today, "once", "medium"))
    owner.add_pet(pet)

    sched = Scheduler(owner)
    plan  = sched.build_priority_schedule(today, max_tasks=2)
    assert len(plan) <= 2