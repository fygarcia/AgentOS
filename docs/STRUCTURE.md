# STRUCTURE.md: File System Organization

```text
/project-root
├── /core                    # The Domain-Agnostic Agentic OS
│   ├── agent.py             # Agent class (owns SkillRegistry)
│   ├── skill_registry.py    # Dynamic skill discovery & loading
│   ├── skill_md_parser.py   # SKILL.md frontmatter parser
│   ├── config.py            # Centralized configuration
│   ├── state.py             # AgentState definition
│   ├── two_stage_client.py  # LLM reasoning + parsing pipeline
│   ├── /nodes               # Planner, Actor, Auditor modules
│   │   ├── planner.py
│   │   ├── actor.py
│   │   └── auditor.py
│   ├── /skills              # Core AgentOS skills (Layer 0)
│   │   ├── /database        # SQLite CRUD operations
│   │   ├── /file-operations # Filesystem I/O (NEW)
│   │   └── /web             # HTTP requests
│   └── /skill_creator       # Tools for creating skills
│       ├── README.md
│       └── /scripts
│           ├── init.py      # Initialize new skill
│           ├── package.py   # Package skill for distribution
│           └── quick_validate.py
│
├── /finn                    # The Financial Agent (Instance)
│   ├── /config              # The "Brain" (Markdown Context)
│   │   ├── AGENTS.md
│   │   ├── SKILLS.md
│   │   ├── AGENT_ORCHESTRATOR.md
│   │   └── PRD.md
│   ├── /directives          # The "Mission" (SOPs)
│   ├── /skills              # Finn-specific skills (Layer 1)
│   │   ├── db_upsert.py
│   │   ├── schema_setup.py
│   │   └── read_portfolio.py
│   ├── /memory              # The "Memory"
│   │   ├── portfolio.db
│   │   └── /vectors
│   └── /inbox               # Watch folder
│
├── /tests                   # Test suite
│   ├── test_core_agentos_workflow.py
│   ├── test_file_operations_skill.py
│   ├── test_skill_intent_recognition.py
│   └── test_integration.py
│
├── /legacy                  # Deprecated / Reference material
│   └── /SKILLS
│
├── .env                     # Environment Variables
├── requirements.txt         # Python dependencies
├── VENV_SETUP.md           # Virtual environment setup
└── .tmp                     # Ephemeral workspace
```