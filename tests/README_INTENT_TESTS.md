# Intent Recognition Test Suite

## Purpose

This test suite validates that the Agent (Planner) correctly:
1. **Understands user intent** from natural language
2. **Identifies appropriate skills** to use
3. **Generates well-structured plans** with correct number of steps

## Test Case Structure

Each test case includes:
- **User Input**: Natural language request
- **Expected Skills**: Which skills should be identified
- **Expected Plan Steps**: Approximate number of steps in plan
- **Tags**: Categories for filtering (e.g., "portfolio", "read", "database")
- **Optional Constraints**: Skills that should NOT be used

## Running Tests

### Using pytest

```powershell
# Run all tests
pytest tests/test_skill_intent_recognition.py -v

# Run specific test
pytest tests/test_skill_intent_recognition.py::TestSkillIntentRecognition::test_tc001_basic_portfolio_read -v

# Run tests with specific tag
pytest tests/test_skill_intent_recognition.py -k "portfolio" -v
```

### Using manual runner

```powershell
# Run all tests
python tests/test_skill_intent_recognition.py --all

# Run specific test case
python tests/test_skill_intent_recognition.py --test TC001

# Run tests by tag
python tests/test_skill_intent_recognition.py --tag portfolio
```

## Current Test Cases

| ID | User Input | Expected Skills | Tags |
|----|-----------|----------------|------|
| TC001 | Show me my portfolio holdings | get_portfolio_holdings | portfolio, read |
| TC002 | What stocks do I own? | get_portfolio_holdings | portfolio, natural_language |
| TC003 | List all my investments | get_portfolio_holdings | portfolio, read |
| TC004 | Add Apple stock | db_upsert_asset | portfolio, write |
| TC005 | I bought 100 shares of TSLA | db_upsert_asset | transaction, write |
| TC006 | Initialize portfolio database | initialize_portfolio_database | database, setup |
| TC007 | Set up tracking system | initialize_portfolio_database | setup, natural_language |
| TC008 | Query Tech sector | sqlite-crud | database, core_skill |
| TC009 | Show database schema | sqlite-crud | database, schema |
| TC010 | Add MSFT and show holdings | db_upsert_asset, get_portfolio_holdings | multi_skill |
| TC011 | Tell me about my portfolio | get_portfolio_holdings | ambiguous |
| TC012 | What's in assets table? | sqlite-crud | database, technical |

## Adding New Test Cases

```python
IntentTestCase(
    id="TC013",
    user_input="Your new test input",
    expected_skills=["skill_name1", "skill_name2"],
    expected_plan_steps=3,
    description="What this test validates",
    tags=["category1", "category2"],
    should_not_use_skills=["forbidden_skill"],  # Optional
    expected_output_type="table"  # Optional
)
```

Then add a test method:

```python
def test_tc013_your_test_name(self):
    """TC013: Your test description"""
    self.test_case(INTENT_TEST_CASES[12])  # Index of your test case
```

## Test Categories

- **portfolio**: Portfolio management operations
- **read**: Read/query operations
- **write**: Create/update operations
- **database**: Database operations
- **core_skill**: Tests for core AgentOS skills
- **natural_language**: Natural language variations
- **multi_skill**: Operations requiring multiple skills
- **ambiguous**: Ambiguous or edge case inputs

## Validation Logic

Each test validates:
1. ✅ All expected skills are identified in the plan
2. ✅ Forbidden skills (if any) are NOT used
3. ✅ Plan step count is within expected range (±1)

## Growing the Test Suite

**When to add new tests:**
- User reports unexpected skill routing
- New skills are added to the system
- Edge cases discovered during development
- A/B testing different phrasing styles

**Best practices:**
- Use realistic user inputs
- Cover both common and edge cases
- Include natural language variations
- Test multi-skill workflows
- Test ambiguous inputs

## Future Enhancements

- [ ] Add output format validation
- [ ] Test skill parameter extraction
- [ ] Validate plan reasoning quality
- [ ] Add performance benchmarks
- [ ] Test error handling scenarios
