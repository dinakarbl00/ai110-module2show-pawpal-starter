import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────
# Streamlit reruns your entire script from top to bottom every
# time a button is clicked. Without session_state, every click
# would create a brand new empty Owner and erase all your data.
#
# Think of st.session_state as a dictionary that Streamlit keeps
# alive between reruns. We store the Owner object there once,
# then read it back on every subsequent rerun.

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="My Household")

owner:     Owner     = st.session_state.owner
scheduler: Scheduler = Scheduler(owner)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🐾 PawPal+")
    st.caption("Smart Pet Care Manager")
    st.divider()

    # ── ADD A PET ─────────────────────────────────────────────
    st.subheader("➕ Add a New Pet")

    with st.form("add_pet_form", clear_on_submit=True):
        p_name    = st.text_input("Pet Name",    placeholder="e.g. Buddy")
        p_species = st.selectbox("Species",      ["dog", "cat", "rabbit", "bird", "fish", "other"])
        p_breed   = st.text_input("Breed",       placeholder="e.g. Labrador")
        p_age     = st.number_input("Age (yrs)", min_value=0, max_value=30, value=1)

        if st.form_submit_button("Add Pet 🐾"):
            if p_name.strip():
                new_pet = Pet(
                    name=p_name.strip(),
                    species=p_species,
                    breed=p_breed.strip() or "Unknown",
                    age=int(p_age),
                )
                owner.add_pet(new_pet)
                st.success(f"Added {new_pet.species_emoji()} **{new_pet.name}**!")
                st.rerun()
            else:
                st.error("Please enter a pet name.")

    st.divider()

    # ── SCHEDULE A TASK ───────────────────────────────────────
    st.subheader("📋 Schedule a Task")

    if not owner.pets:
        st.info("Add a pet first!")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            t_pet      = st.selectbox("For Pet",      [p.name for p in owner.pets])
            t_desc     = st.text_input("Description", placeholder="e.g. Morning walk")
            t_type     = st.selectbox("Task Type",    ["walk", "feeding", "medication", "vet", "general"])
            t_time     = st.time_input("Time")
            t_date     = st.date_input("Date", value=date.today())
            t_freq     = st.selectbox("Frequency",    ["once", "daily", "weekly"])
            t_priority = st.selectbox("Priority",     ["high", "medium", "low"])

            if st.form_submit_button("Add Task ✅"):
                if t_desc.strip() and t_time:
                    pet = owner.get_pet(t_pet)
                    pet.add_task(Task(
                        description=t_desc.strip(),
                        due_time=t_time.strftime("%H:%M"),
                        due_date=str(t_date),
                        frequency=t_freq,
                        priority=t_priority,
                        task_type=t_type,
                    ))
                    st.success(f"Task added to **{t_pet}**!")
                    st.rerun()
                else:
                    st.error("Please fill in description and time.")

    st.divider()

    # ── RESET ─────────────────────────────────────────────────
    if st.button("Reset Everything 🗑️"):
        st.session_state.owner = Owner(name="My Household")
        st.rerun()


# ──────────────────────────────────────────────────────────────
# MAIN AREA
# ──────────────────────────────────────────────────────────────

st.title("🐾 PawPal+ Dashboard")
st.caption(f"Today — {date.today().strftime('%A, %B %d, %Y')}")

st.divider()

# ── TABS ──────────────────────────────────────────────────────

tab1, tab2 = st.tabs(["📅 Today's Tasks", "🐾 My Pets"])


# ── TAB 1: TODAY'S TASKS ──────────────────────────────────────

with tab1:
    st.subheader("📅 Today's Tasks")
    st.caption("Tasks for today across all pets.")

    todays_tasks = [
        (pet_name, task)
        for pet_name, task in owner.get_all_tasks()
        if task.due_date == str(date.today())
    ]

    if not todays_tasks:
        st.info("No tasks scheduled for today. Add some in the sidebar!")
    else:
        for pet_name, task in todays_tasks:
            with st.container(border=True):
                cols = st.columns([0.5, 3.5, 1, 1.2, 1.8])
                cols[0].write(f"{task.priority_emoji()} {task.emoji()}")
                cols[1].write(f"**{pet_name}** — {task.description}")
                cols[2].write(f"`{task.due_time}`")
                cols[3].write(task.frequency)

                if not task.completed:
                    btn_key = f"done_{pet_name}_{task.task_id}"
                    if cols[4].button("Mark Done ✅", key=btn_key):
                        task.mark_complete()
                        st.success(f"✅ '{task.description}' marked complete!")
                        st.rerun()
                else:
                    cols[4].success("Done ✅")


# ── TAB 2: MY PETS ────────────────────────────────────────────

with tab2:
    st.subheader("🐾 My Pets")

    if not owner.pets:
        st.info("No pets yet. Add one using the sidebar!")
    else:
        cols = st.columns(min(len(owner.pets), 3))
        for i, pet in enumerate(owner.pets):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"### {pet.species_emoji()} {pet.name}")
                    st.write(f"**Species:** {pet.species.title()}")
                    st.write(f"**Breed:**   {pet.breed}")
                    st.write(f"**Age:**     {pet.age} yr{'s' if pet.age != 1 else ''}")
                    pending = len(pet.get_pending_tasks())
                    done    = len(pet.get_completed_tasks())
                    st.write(f"**Tasks:**   {pending} pending, {done} done")

                    if pet.tasks:
                        with st.expander("View all tasks"):
                            for task in pet.tasks:
                                status = "✅" if task.completed else "⬜"
                                st.write(
                                    f"{status} {task.priority_emoji()} {task.emoji()} "
                                    f"`{task.due_time}` {task.description}"
                                )

                    if st.button(f"Remove {pet.name} 🗑️", key=f"rm_{pet.name}"):
                        owner.remove_pet(pet.name)
                        st.rerun()