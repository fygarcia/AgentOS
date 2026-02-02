# SKILLS.md: Deterministic Tool Registry

| Category | Skill Name | Script Path | Description |
| :--- | :--- | :--- | :--- |
| **Data** | `ingest_raw_data` | `execution/ingest.py` | Normalizes CSV/PDF to intermediate JSON. |
| **Data** | `update_portfolio` | `execution/db_upsert.py` | Writes normalized data to SQLite. |
| **Finance** | `calculate_yield` | `execution/finance_math.py` | Deterministic bond yield/PnL math. |
| **Research** | `search_market` | `execution/web_tool.py` | Fetches news via Tavily/SearXNG. |
| **System** | `create_skill` | `finn/skills/skill_creator/scripts/init.py` | Initialize a new skill. Planner calls this when a new capability is needed. |

## Rules for Skill Creation
1. All scripts must use `decimal` for currency—NEVER floats.
2. Every script must return a standard JSON object: `{"status": "success/error", "data": {...}, "log": "..."}`.
3. If a script fails 3 times, the agent must escalate to the **Self-Healing Loop**.