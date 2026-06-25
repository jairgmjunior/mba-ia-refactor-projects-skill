# Report Template: Architecture Audit Report Format

Use this template format for Fase 2 output (Architecture Audit Report).

---

```
================================
ARCHITECTURE AUDIT REPORT
================================

## Project Information
- **Name:** [project-name]
- **Stack:** [Language] + [Framework]  
- **Database:** [SQLite/PostgreSQL/MongoDB/...]
- **Domain:** [Brief description of app purpose]
- **Total Files Analyzed:** [N] source files
- **Approx. Lines of Code:** [estimate]

---

## Executive Summary

| Severity | Count |
|:---:|:---:|
| CRITICAL | [N] |
| HIGH | [N] |
| MEDIUM | [N] |
| LOW | [N] |
| **TOTAL** | **[N]** |

**Overall Assessment:** [1-2 sentence summary of main issues]

---

## Detailed Findings

### [CRITICAL] Finding Title
**File:** [path/file.py:line-range]  
**Description:** [Specific description of the issue]  
**Impact:** [How this affects the project]  
**Recommendation:** [What to do]  
**Example (current code):**
\`\`\`
[code snippet showing the problem]
\`\`\`

---

### [CRITICAL] Second Finding
[Same format...]

---

### [HIGH] Finding Title
**File:** [path/file.js:line-range]  
[Details...]

---

### [HIGH] Second Finding
[Details...]

---

### [MEDIUM] Finding Title
[Details...]

---

### [MEDIUM] Second Finding
[Details...]

---

### [LOW] Finding Title
[Details...]

---

### [LOW] Second Finding
[Details...]

---

## Refactoring Recommendations

### Priority 1: Address CRITICAL Issues
1. [Issue 1] — Risk of [consequence]
2. [Issue 2] — Affects [area]
3. [Issue 3] — Violates [principle]

### Priority 2: Address HIGH Issues
1. [Issue 4] — Impacts [area]
2. [Issue 5] — Causes [problem]
3. [Issue 6] — Breaks [principle]

### Priority 3: Address MEDIUM Issues
1. [Issue 7] — Reduces [quality aspect]
2. [Issue 8] — Affects [area]
3. [Issue 9] — Causes [problem]

### Priority 4: Address LOW Issues
1. [Issue 10] — Improves [readability/maintainability]
2. [Issue 11] — Better [practice]

---

## Architecture Transformation Plan

### Current Architecture
```
[Current structure tree]
```

### Target Architecture (MVC)
```
src/
├── config/
│   ├── settings.py
│   └── database.py
├── models/
│   ├── __init__.py
│   └── [entities].py
├── controllers/
│   ├── __init__.py
│   └── [domain]_controller.py
├── views/ (or routes/)
│   ├── __init__.py
│   └── [domain]_routes.py
├── middleware/
│   ├── __init__.py
│   ├── error_handler.py
│   └── auth.py
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   └── helpers.py
├── app.py
└── main.py
```

### Transformation Steps
1. [Step 1] — Extract config
2. [Step 2] — Separate models
3. [Step 3] — Create controllers
4. [Step 4] — Organize routes
5. [Step 5] — Add middleware
6. [Step 6] — Centralize utilities

---

## Estimated Effort

| Task | Effort | Priority |
|:---|:---:|:---:|
| Fix CRITICAL issues | [X hours] | MUST |
| Fix HIGH issues | [X hours] | SHOULD |
| Fix MEDIUM issues | [X hours] | COULD |
| Fix LOW issues | [X hours] | NICE-TO-HAVE |
| **Total** | **[X hours]** | - |

---

## Validation Checklist (Post-Refactor)

- [ ] Application starts without errors
- [ ] All endpoints respond correctly
- [ ] Database initializes properly
- [ ] No hardcoded secrets in code
- [ ] SQL queries parameterized
- [ ] Clear separation of concerns (M/C/V)
- [ ] Error handling centralized
- [ ] Duplicate code eliminated
- [ ] Magic numbers/strings extracted to constants
- [ ] Variable names clarified
- [ ] Unnecessary imports removed

---

## Next Steps

1. **Review** this report
2. **Confirm** you want to proceed with refactoring
3. **Execute** Fase 3 (Refactoring)
4. **Validate** result with checklist above
5. **Test** all endpoints respond as before

---

## Files Affected by Refactoring

The following transformations will be applied:

| Anti-Pattern | Affected File | Transformation |
|:---|:---|:---|
| [Pattern] | [file.py] | [What will change] |
| [Pattern] | [file.js] | [What will change] |
| ... | ... | ... |

---

**Generated:** [timestamp]  
**Project:** [project-name]  
**Analyst:** Architectural Audit Skill
```

---

## Usage Instructions

1. **Before Phase 2 begins**, you have the template above
2. **As you scan**, fill in:
   - Project name, stack, database, domain
   - Count findings by severity
   - For each finding: file:line, description, impact, recommendation
3. **Order findings**: CRITICAL → HIGH → MEDIUM → LOW
4. **Provide examples**: Show problematic code snippets
5. **Suggest refactoring**: Reference the playbook
6. **Present to user**: Ask for confirmation before Phase 3

---

## Key Requirements

✅ **File and Line Numbers:** MUST be exact (file.py:8-15, not "around line 8")  
✅ **Ordered by Severity:** CRITICAL first, LOW last  
✅ **Minimum 5 findings:** Across all severities  
✅ **Minimum 1 CRITICAL/HIGH:** Required in every report  
✅ **User Confirmation:** Always pause before Phase 3  
✅ **Specific Examples:** Show code snippets, not generic descriptions  
✅ **Clear Impact:** Explain why each issue matters  
✅ **Actionable Recommendations:** Reference playbook transformations  

---

## Example Report (Condensed)

```
================================
ARCHITECTURE AUDIT REPORT
================================

Project: code-smells-project
Stack: Python + Flask
Database: SQLite
Domain: E-commerce API
Files Analyzed: 4

## Summary
CRITICAL: 3 | HIGH: 2 | MEDIUM: 2 | LOW: 1

## Findings

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded as 'minha-chave-super-secreta-123'
Impact: If code leaked, attacker gains session signing capability
Recommendation: Move to environment variable
Example:
  app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"  ← WRONG

### [CRITICAL] SQL Injection
File: models.py:28
Description: query "SELECT * FROM produtos WHERE id = " + str(id)
Impact: Attacker can execute arbitrary SQL queries
Recommendation: Use parameterized queries with ?
Example:
  cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))  ← WRONG

### [CRITICAL] God Class
File: app.py:1-89
Description: File contains routing, config, health, and admin endpoints all mixed
Impact: Impossible to test independently, any change affects everything
Recommendation: Separate into models/controllers/routes

### [HIGH] Direct DB Access
File: controllers.py:1-100
Description: Controllers execute SQL queries directly (cursor.execute in controllers)
Impact: Hard to test, DB logic scattered everywhere
Recommendation: Create models/repository layer

### [HIGH] Missing Separating Concerns
File: controllers.py:1-100
Description: Validation, DB access, HTTP response all in same function
Impact: Cannot reuse validation logic, hard to unit test
Recommendation: Extract validation to separate layer, use service classes

### [MEDIUM] Duplicated Validation
File: controllers.py (multiple functions)
Description: Product validation (name, price, stock checks) repeated in criar_produto, atualizar_produto, etc.
Impact: If validation needs change, must update multiple places
Recommendation: Extract to utils/validators.py

### [MEDIUM] Magic Strings
File: controllers.py:45-60
Description: categorias_validas = ["informatica", "moveis", ...] hardcoded in multiple places
Impact: No single source of truth for categories
Recommendation: Move to config/constants.py

### [LOW] Unused Import
File: models.py:1
Description: import sqlite3 — not used, only using database.py's connection
Impact: Unclear dependencies
Recommendation: Remove unused import

---

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
