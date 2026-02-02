# Venv Setup Instructions

**⚠️ NOTE:** Dependencies were installed globally during development. 
For production, use venv:

## Setup Virtual Environment

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pydantic, yaml; print('✅ Dependencies OK')"
```

## Dependencies Installed (Jan 31, 2026)

- `python-dotenv` - Environment configuration
- `PyYAML` - SKILL.md frontmatter parsing
- `pydantic` - Data validation
- `pydantic-ai` - LLM framework

## Running Tests

```powershell
# Activate venv first!
.\venv\Scripts\Activate.ps1

# Run integration test
python test_integration.py

# Run skill registry test
python core\skill_registry.py

# Run agent test
python -m core.agent
```

## For Future Work

Always activate venv before installing packages:
```powershell
.\venv\Scripts\Activate.ps1
pip install <package>
```
