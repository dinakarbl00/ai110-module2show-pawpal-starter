# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?
- A:    I designed four classes for this scenario. 
Task: this is responsible for the details about the work, such as description, due time, due date, frequency, priority, completed and task type.
Pet: this is responsible for the pet's identity, such as name, species, breed and age. It also has a list of Task objects.
Owner: this is the top-level data store. It holds pets and provides get_all_tasks(), which flattens every pet's tasks into one flat list of (pet_name, Task) tuples. This single method is the only way the Scheduler reads data, which keeps the two classes loosely coupled.
Scheduler: this is more of a business logic. The Scheduler holds no data; it only reads from Owner and returns results. This makes it easy to test and extend.

Core action for users:
1. Add a pet with identifying information (name, species, breed, age)
2. Schedule a care task for a pet (description, time, date, frequency, priority)
3. View today's schedule sorted and filtered in a useful, prioritised way

**b. Design changes**

- Did your design change during implementation?
- A: Yes
- If yes, describe at least one change and why you made it.
- A: Added task_id to Task class. This was because I needed a way to uniquely identify tasks for editing and deleting, and the combination of description and due time was not guaranteed to be unique. Adding a task_id made it easier to manage tasks without relying on potentially ambiguous attributes.
I will be using explicit list type hints instead of generic list returns. This is because it provides more clarity on what type of data is being returned, which can help with debugging and understanding the code.
I accepted these changes while I rejected Date/time as string fields. Copilot suggested parsing `due_time` and `due_date` into proper datetime objects at creation time. I rejected this because zero-padded HH:MM strings sort correctly using plain string comparison, and adding `__post_init__` validation would increase complexity without meaningful benefit at this project's scale.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- A: The scheduler considers time, date, priority level, and task type.
- How did you decide which constraints mattered most?
- A: Priority was chosen as the primary sort key over time because a high-priority
vet appointment at 14:00 is more important to surface than a low-priority
walk at 07:00. Time acts as a tiebreaker within each priority band.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- A: Conflict detection uses exact time matching, not duration-based overlap.
Two tasks are only flagged as conflicting if they share the exact same. A walk at 08:00 and a grooming at 08:15 would not be flagged even if the walk takes 45 minutes. 
- Why is that tradeoff reasonable for this scenario?
- A: This is reasonable here because most pet care tasks are instant events rather than extended blocks. Asking users to estimate duration for every task adds friction for little gain. The most
common real mistake of double-booking the exact same slot is fully caught.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- A: I used copilot for design review, generating code snippets, test cases, and refactoring suggestions.
In the skeleton phase I asked Copilot to review `pawpal_system.py` using `#file:pawpal_system.py` and report any missing relationships or logic bottlenecks. It returned four ranked findings which directly shaped the final design.
For `to_dict()` and `from_dict()` serialisation methods on Task, Pet, and Owner, I asked Copilot to generate them from the class attributes. These are mechanical but tedious to write correctly; the output was accurate and accepted with minor edits.
For `find_next_available_slot()` I described the goal to Agent Mode and asked it to compare strategies. It offered a nested loop and a hash-set approach, explained the trade-off, and scaffolded the hash-set version. I reviewed the edge cases manually before accepting.
- What kinds of prompts or questions were most helpful?
- A: The most effective prompt pattern was: state the goal + constraints + where the code should go. For example: "Implement a conflict checker inside the Scheduler class that returns warning strings instead of raising exceptions, using a dict to group tasks by (date, time) slot."

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- A: When I first asked for conflict detection logic, Copilot generated a nested loop that compared every task against every other task. It was correct but O(n²) and produced duplicate warnings. I replaced it with the single-pass dictionary approach: build a dict keyed by `(date, time)`, then flag any key with two or more entries. This is O(n), produces each conflict exactly once, and reads more clearly.
- How did you evaluate or verify what the AI suggested?
- A: I verified the replacement manually by tracing through the example with one deliberate conflict before running the tests.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- A: Behaviors tested are task completion, adding tasks to a pet, sorting correctness , recurring rescheduling, conflict detection, filtering, edge cases, JSON persistence, and the priority-weighted schedule.
- Why were these tests important?
- A: These are important because the algorithmic methods have subtle correctness requirements that are easy to get slightly wrong.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- A: I am very confident that my scheduler works correctly for the tested cases, but there may be edge cases I haven't considered. 
- What edge cases would you test next if you had more time?
- A: Edge cases I would explore next with more time: tasks with malformed due_time strings, weekly tasks that recur across a year boundary, saving and loading while the Streamlit app is running simultaneously, and how the system handles daylight saving time changes.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
- A: the initial design, class structure and brainstorming. I think the separation of concerns between Owner and Scheduler was a good choice that made the logic easier to implement and test. The Owner class acts as a clean data store, while the Scheduler focuses solely on the scheduling logic without needing to manage data directly. The test suite also gave real confidence. Every time I made changes, I could immediately run `pytest` and know whether I had broken anything. That feedback loop made the whole build feel much more controlled.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
- A: I would add a `duration_minutes` field to Task in the next iteration. This would enable proper overlap-based conflict detection.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
- A: AI is excellent at implementing decisions but poor at making them. Given a precise goal with constraints it produced correct code quickly. Every time I asked "what should I do here?" the suggestions were too generic to use directly.
