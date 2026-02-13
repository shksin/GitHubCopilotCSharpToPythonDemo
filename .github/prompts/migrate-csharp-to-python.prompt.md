# GitHub Copilot Custom Instruction  
## C# → Python Migration (With Plan & Summary)

---

## 🎯 Primary Goals

- Maintain the same functionality and behavior as the original C# code.
- Write clean, readable, and Pythonic code.
- Keep the solution simple and maintainable.

---

## 🧭 Step 1 – Create Migration Plan (**MANDATORY**)

Before writing or converting any code:

### Analyse the provided C# code and produce a migration plan including:

1. **High-level understanding** of the C# solution  
2. **File/module mapping**  
   - C# files → Python modules  
3. **Data model and class conversion approach**
4. **Dependency and library replacements**
5. **Async/concurrency conversion approach** (if applicable)
6. **Error handling and exception mapping**
7. **Testing strategy**
8. **Assumptions or risks**

### ❗ Approval Gate

- Stop after generating the migration plan  
- Wait for **explicit user approval** before proceeding  
- **Do NOT generate Python code until approval is received**

---

## 🔄 Step 2 – Perform Migration

After user approval:

- Convert the code following the approved migration plan
- Maintain behavioral parity with the original implementation
- Use Pythonic patterns without unnecessary complexity

---

### Migration Guidelines

- Convert C# classes into Python classes  
  - Use `dataclasses` when suitable
- Convert interfaces into:
  - Base classes  
  - `typing.Protocol` when appropriate
- Replace LINQ with:
  - Python list/dictionary comprehensions  
  - Built-in functions
- Convert async/await logic to Python `asyncio`
- Use Python exception handling instead of C# exception patterns
- Avoid unnecessary frameworks unless required
- Migrate all unit tests to Python using `pytest`
- Ensure all tests pass and provide similar coverage as the original C# tests
- Convert C# `appsettings.json` / `IConfiguration` settings to flat environment variables in a `.env` file
- Add `python-dotenv` to `requirements.txt` and call `load_dotenv()` at application startup

---

### Coding Standards

- Use **type hints** for parameters and return types
- Add **docstrings** to public classes and functions
- Use Python **logging** instead of print statements
- Do not hardcode secrets  
  - Use `.env` files or environment variables
  - Never commit `.env` files containing real secrets — add `.env` to `.gitignore`
- Prefer Python **standard libraries** where possible

---

### Testing

- Include unit tests using **pytest**
- Include tests when creating or migrating modules

---

## 📊 Step 3 – Create Migration Summary (**MANDATORY**)

After completing the migration, generate a summary including:

1. **Files converted**
2. **Key design or architectural changes**
3. **Behavior differences** (if any)
4. **Dependencies replaced or introduced**
5. **Known limitations or follow-up recommendations**
6. **Testing coverage summary**
7. **Assumptions made during migration**

---

## 🧠 General Behaviour

- Preserve input/output behavior unless explicitly stated
- Keep code simple and easy to understand
- Clearly explain uncertainties or assumptions
