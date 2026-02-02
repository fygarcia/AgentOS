# SELF_HEALING.md: The Annealing Protocol

## The "Actor-Auditor" Loop
When a task is executed, it must pass through this loop:

1. **Execution:** The **Actor** runs a Python script from `execution/`.
2. **Audit:** The **Auditor** compares the script's output with the raw input file.
3. **Verification:**
    - If `Match`: Move to next task.
    - If `Mismatch`: Log the error and identify the "Delta" (what went wrong).

## Healing Steps
1. **Diagnosis:** Read the Python Traceback + the mismatched data.
2. **Patching:** The **Actor** creates a temporary fix (e.g., `execution/temp_fix.py`).
3. **Validation:** Run the fix against the current data.
4. **Promotion:** Overwrite the old script and update the version in `SKILLS.md`.
5. **Instruction Update:** Update the corresponding `Directive` so the agent "remembers" the fix.