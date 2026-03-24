"""
main.py — PawPal+ CLI Demo
============================
Tests that Owner, Pet, and Task all work correctly in the terminal.
Run with:  python main.py
"""

from datetime import date, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def banner(title: str) -> None:
    print(f"\n{'═' * 58}")
    print(f"  🐾  {title}")
    print(f"{'═' * 58}")


def print_tasks(title: str, task_list: list) -> None:
    """Print a readable list of (pet_name, Task) tuples."""
    print(f"\n  ── {title}")
    if not task_list:
        print("    (no tasks)")
        return
    for pet_name, task in task_list:
        status = "✅" if task.completed else "⬜"
        print(
            f"  {status} {task.priority_emoji()} {task.emoji()}  "
            f"[{task.due_time}]  {pet_name:10}  {task.description}"
        )


# ─────────────────────────────────────────────────────────────
# 1. CREATE OWNER AND PETS
# ─────────────────────────────────────────────────────────────

banner("1 · Create Owner & Pets")

owner = Owner(name="Jordan Lee", email="jordan@example.com")

buddy    = Pet(name="Buddy",    species="dog",    breed="Labrador",    age=3)
whiskers = Pet(name="Whiskers", species="cat",    breed="Siamese",     age=5)
thumper  = Pet(name="Thumper",  species="rabbit", breed="Holland Lop", age=2)

owner.add_pet(buddy)
owner.add_pet(whiskers)
owner.add_pet(thumper)

print(f"  Owner : {owner.name}  ({owner.email})")
print(f"  Pets  : {owner.pet_count()} registered")
for pet in owner.pets:
    print(f"          {pet.species_emoji()}  {pet.name} — {pet.breed}, age {pet.age}")


# ─────────────────────────────────────────────────────────────
# 2. ADD TASKS
# ─────────────────────────────────────────────────────────────

banner("2 · Add Tasks")

today = str(date.today())

buddy.add_task(Task("Morning walk",      "07:30", today, "daily",  "high",   task_type="walk"))
buddy.add_task(Task("Breakfast feeding", "08:00", today, "daily",  "high",   task_type="feeding"))
buddy.add_task(Task("Heartworm pill",    "09:00", today, "weekly", "high",   task_type="medication"))
buddy.add_task(Task("Evening walk",      "18:00", today, "daily",  "medium", task_type="walk"))

whiskers.add_task(Task("Breakfast feeding", "08:00", today, "daily",  "high",   task_type="feeding"))
whiskers.add_task(Task("Flea medication",   "09:30", today, "weekly", "medium", task_type="medication"))
whiskers.add_task(Task("Playtime",          "15:00", today, "daily",  "low",    task_type="general"))

thumper.add_task(Task("Morning feeding", "07:00", today, "daily",  "high",   task_type="feeding"))
thumper.add_task(Task("Cage cleaning",   "11:00", today, "weekly", "medium", task_type="general"))
thumper.add_task(Task("Evening feeding", "18:00", today, "daily",  "high",   task_type="feeding"))

print(f"  Buddy    — {buddy.task_count()} tasks")
print(f"  Whiskers — {whiskers.task_count()} tasks")
print(f"  Thumper  — {thumper.task_count()} tasks")


# ─────────────────────────────────────────────────────────────
# 3. VIEW ALL TASKS VIA OWNER
# ─────────────────────────────────────────────────────────────

banner("3 · All Tasks via get_all_tasks()")

print_tasks("Every task across all pets", owner.get_all_tasks())


# ─────────────────────────────────────────────────────────────
# 4. MARK COMPLETE + RESCHEDULING
# ─────────────────────────────────────────────────────────────

banner("4 · Mark Complete & Reschedule")

# Mark Buddy's first task complete
result = buddy.tasks[0].mark_complete()
print(f"\n  {result}")

# Check pending / completed split
print(f"  Buddy pending   : {len(buddy.get_pending_tasks())}")
print(f"  Buddy completed : {len(buddy.get_completed_tasks())}")

# Verify daily task reschedules to tomorrow
tomorrow  = str(date.today() + timedelta(days=1))
next_task = buddy.tasks[0].reschedule()

print(f"\n  Reschedule check (daily task):")
print(f"    Original date : {buddy.tasks[0].due_date}")
print(f"    Next date     : {next_task.due_date}  ← should be {tomorrow}")
print(f"    Fresh task_id : {next_task.task_id[:8]}...  ← different from original")

# Verify one-time task does NOT reschedule
vet = Task("Vet checkup", "10:00", today, "once", "high", task_type="vet")
print(f"\n  Reschedule check (once task): {vet.reschedule()}  ← should be None ✅")


# ─────────────────────────────────────────────────────────────
# 5. PENDING / COMPLETED FILTERS
# ─────────────────────────────────────────────────────────────

banner("5 · Pending and Completed Filters")

print(f"\n  Buddy total     : {buddy.task_count()}")
print(f"  Buddy pending   : {len(buddy.get_pending_tasks())}")
print(f"  Buddy completed : {len(buddy.get_completed_tasks())}")

print("\n  Pending:")
for t in buddy.get_pending_tasks():
    print(f"    {t.priority_emoji()} {t.emoji()}  {t.description}")

print("\n  Completed:")
for t in buddy.get_completed_tasks():
    print(f"    ✅  {t.description}")


# ─────────────────────────────────────────────────────────────
# 6. REMOVE A TASK
# ─────────────────────────────────────────────────────────────

banner("6 · Remove a Task")

before  = whiskers.task_count()
removed = whiskers.remove_task("Playtime")
after   = whiskers.task_count()

print(f"  Removed 'Playtime' : {removed}  ← should be True ✅")
print(f"  Whiskers tasks     : {before} → {after}")

not_found = whiskers.remove_task("Does not exist")
print(f"  Remove missing     : {not_found}  ← should be False ✅")


# ─────────────────────────────────────────────────────────────
# 7. OWNER HELPERS
# ─────────────────────────────────────────────────────────────

banner("7 · Owner Helpers")

found     = owner.get_pet("buddy")
not_found = owner.get_pet("Nemo")

print(f"  get_pet('buddy') : {found.name if found else None}  ← should be Buddy ✅")
print(f"  get_pet('Nemo')  : {not_found}  ← should be None ✅")
print(f"  pet_count()      : {owner.pet_count()}  ← should be 3 ✅")


# ─────────────────────────────────────────────────────────────
# 8. EMOJI DISPLAY
# ─────────────────────────────────────────────────────────────

banner("8 · Emoji Display")

samples = [
    Task("Walk",      "07:00", today, priority="high",   task_type="walk"),
    Task("Feed",      "08:00", today, priority="high",   task_type="feeding"),
    Task("Give pill", "09:00", today, priority="high",   task_type="medication"),
    Task("Vet visit", "10:00", today, priority="medium", task_type="vet"),
    Task("Play",      "15:00", today, priority="low",    task_type="general"),
]

print()
for t in samples:
    print(f"  {t.priority_emoji()} {t.emoji()}  {t.description:12}  priority={t.priority}")


print("\n\n  🎉  Demo complete — core classes are working!\n")