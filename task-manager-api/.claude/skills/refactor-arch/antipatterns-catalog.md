# Anti-Patterns Catalog

Complete catalog of 10+ anti-patterns with detection signals, severity classification, and recommendations.

---

## CRITICAL Severity

### 1. Hardcoded Credentials & Secrets

**Description:** Sensitive information (API keys, passwords, tokens) hardcoded directly in source code.

**Severity:** CRITICAL â€” Exposes secrets if code is compromised, enables unauthorized access.

**Detection Signals:**
- Python:
  - `SECRET_KEY = "string"`
  - `PASSWORD = "..."`
  - `API_KEY = "..."`
  - `app.config["SECRET_KEY"] = "..."`
  - Database password in connection string
  
- Node.js:
  - `const config = { password: "..." }`
  - `const apiKey = "pk_live_..."`
  - Credentials in utils.js or config object
  - Database URL hardcoded

**Search patterns:**
```
- Line contains: SECRET_KEY, PASSWORD, API_KEY, dbPass, apiKey
- Value is string literal (not process.env, not os.environ)
- Appears to be in root config or utils file
```

**Example (Bad):**
```python
# app.py
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
db_password = 'root123'
```

**Example (Good):**
```python
# config/settings.py
import os
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
db_password = os.environ.get('DB_PASSWORD')
```

**Recommendation:** Extract to environment variables, use `.env` file with `python-dotenv` or Node.js `dotenv`.

---

### 2. SQL Injection Vulnerability

**Description:** User input directly concatenated into SQL queries without parameterization.

**Severity:** CRITICAL â€” Allows attackers to execute arbitrary SQL, steal/modify/delete data.

**Detection Signals:**
- Python:
  - `execute("SELECT * FROM " + table)`
  - `execute(f"WHERE id = {id}")`
  - `execute("WHERE email = '" + email + "'")`
  - String concatenation in SQL
  - No use of `?` or `%s` placeholders
  
- Node.js:
  - `db.run("INSERT INTO users VALUES (" + id + ")")`
  - Template literals with variables in SQL
  - No use of parameterized queries

**Search patterns:**
```
- Line contains: execute(), run(), query()
- AND contains: + or f-string with variable
- NOT contains: `?`, `%s`, `$1` (placeholder)
- AND variable appears to come from user input (request, params)
```

**Example (Bad):**
```python
# models.py
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO usuarios (email, senha) VALUES ('" + email + "', '" + senha + "')")
```

**Example (Good):**
```python
# models.py
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("INSERT INTO usuarios (email, senha) VALUES (?, ?)", (email, senha))
```

**Recommendation:** Always use parameterized queries or ORM (SQLAlchemy, Sequelize).

---

### 3. God Class / God Method

**Description:** Single class or file with excessive responsibilities (routing, DB access, business logic, validation all mixed).

**Severity:** CRITICAL â€” Impossible to test in isolation, violates Single Responsibility Principle, affects any change.

**Detection Signals:**
- Single file (e.g., `AppManager.js`, `models.py`) contains:
  - HTTP route definitions
  - Database queries
  - Business logic
  - Validation rules
  - Error handling
  - Configuration
  
- Typical file > 200 lines with mixed concerns
- Methods handle multiple unrelated tasks

**Search patterns:**
```
- File exists: app.py, models.py, AppManager.js, GodManager.js
- Contains multiple @app.route() or app.get()
- Contains database operations (cursor.execute, db.run)
- Contains validation logic
- Contains business calculations
- All in ONE file
```

**Example (Bad):**
```python
# app.py â€” Everything mixed
class AppManager:
    def __init__(self):
        self.db = sqlite3.Database(':memory:')
    
    def setup_routes(self, app):  # Routing setup
        app.post('/checkout', self.checkout)  # Routes
    
    def checkout(self):  # Business logic
        # DB queries
        self.db.execute("SELECT * FROM courses")
        # Validation
        if not user: raise Error
        # Calculations
        total = course.price * qty
        # More DB
        self.db.execute("INSERT INTO orders")
        # Audit logging
        self.log_audit(action)
```

**Example (Good):**
```python
# controllers/checkout_controller.py
class CheckoutController:
    def __init__(self, order_service, payment_service):
        self.order_service = order_service
        self.payment_service = payment_service
    
    def checkout(self, user_id, course_id):
        # Orchestrates services
        course = self.course_service.get_course(course_id)
        order = self.order_service.create_order(user_id, course)
        payment = self.payment_service.process_payment(order)
        return payment

# views/checkout_routes.py
@app.post('/checkout')
def checkout():
    controller = CheckoutController(...)
    return controller.checkout(...)
```

**Recommendation:** Separate into Models (data), Controllers (logic), Views (routes). Use Dependency Injection.

---

## HIGH Severity

### 4. Direct Database Access Without Abstraction

**Description:** Controllers/Routes directly execute SQL queries without using Models or Data Access Layer.

**Severity:** HIGH â€” Tightly coupled, difficult to test, hard to migrate databases.

**Detection Signals:**
- Controllers contain `cursor.execute()`, `db.run()`, `query()` calls
- SQL queries scattered across multiple files
- No abstraction layer (no Repository, no DAO, no ORM properly used)
- Each route has its own query logic

**Search patterns:**
```
- File: controllers.py, routes/*, app.js
- Contains: cursor.execute(), db.run(), db.query(), connection.query()
- Directly accesses database object
```

**Example (Bad):**
```python
# controllers.py
def criar_produto():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos ...")  # â† Direct DB access
    db.commit()
```

**Example (Good):**
```python
# controllers/produto_controller.py
def criar_produto(data):
    produto = Produto.create(data)  # â† Uses Model

# models/produto_model.py
class Produto(db.Model):
    @staticmethod
    def create(data):
        produto = Produto(**data)
        db.session.add(produto)
        db.session.commit()
        return produto
```

**Recommendation:** Create Model/Repository layer that encapsulates DB operations.

---

### 5. Callback Hell / Deeply Nested Callbacks

**Description:** Multiple nested async callbacks making code hard to read and maintain.

**Severity:** HIGH â€” Error handling difficult, callback chains error-prone.

**Detection Signals:**
- Node.js code
- Multiple levels of `function(err, result) { ... function() { ... } }`
- Callback functions nested 3+ levels deep
- Error handling repeated or missing
- No use of async/await or Promises

**Search patterns:**
```
- Contains: callback(function() { ... function() { ... function() { ... } } })
- Multiple levels of indentation
- Error handling scattered
```

**Example (Bad):**
```javascript
// AppManager.js
app.post('/checkout', (req, res) => {
    let userId = req.body.usr;
    
    db.get("SELECT * FROM courses WHERE id = ?", [courseId], (err, course) => {
        if (err) return res.status(500).send("Error");
        
        db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
            if (err) return res.status(500).send("Error");
            
            if (!user) {
                db.run("INSERT INTO users ...", (err) => {
                    if (err) return res.status(500).send("Error");
                    
                    db.run("INSERT INTO enrollments ...", (err) => {
                        // ... more nesting
                    });
                });
            }
        });
    });
});
```

**Example (Good):**
```javascript
// controllers/checkoutController.js
async function checkout(req, res) {
    try {
        const course = await Course.findById(req.body.courseId);
        let user = await User.findByEmail(req.body.email);
        
        if (!user) {
            user = await User.create({...});
        }
        
        const enrollment = await Enrollment.create({userId: user.id, ...});
        res.json({success: true, enrollmentId: enrollment.id});
    } catch (err) {
        next(err);
    }
}
```

**Recommendation:** Convert to async/await or Promises. Centralize error handling with middleware.

---

### 6. Global Mutable State

**Description:** Global variables holding application state that can be mutated from anywhere.

**Severity:** HIGH â€” Causes unexpected behavior, difficult debugging, breaks in concurrent execution.

**Detection Signals:**
- Global variable assignments (not constants)
- Multiple functions/modules modify same global
- No encapsulation or getter/setter
- Used for caching, counters, flags

**Search patterns:**
```
- File level: let globalCache = {}
- File level: let totalRevenue = 0
- Multiple files modify these globals
- No locks or synchronization
```

**Example (Bad):**
```python
# database.py
db_connection = None  # Global mutable

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(...)
    return db_connection
```

```javascript
// utils.js
let globalCache = {};
let totalRevenue = 0;

function logAndCache(key, data) {
    globalCache[key] = data;  // â† Mutates global
}

module.exports = { globalCache, totalRevenue };
```

**Example (Good):**
```python
# config/database.py
class DatabaseConnection:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = sqlite3.connect(...)
        return cls._instance

db = DatabaseConnection.get_instance()
```

```javascript
// services/cacheService.js
class CacheService {
    constructor() {
        this.cache = {};
    }
    
    set(key, value) {
        this.cache[key] = value;
    }
}

module.exports = new CacheService();
```

**Recommendation:** Use Singleton pattern, Dependency Injection, or encapsulated services.

---

## MEDIUM Severity

### 7. N+1 Query Problem

**Description:** Loop fetching data where each iteration executes a separate query (1 initial + N queries for N items).

**Severity:** MEDIUM â€” Performance degradation, can cause timeouts with large datasets.

**Detection Signals:**
- Loop over collection (courses, products, users)
- Inside loop: database query for each item
- Typically: `for item in items: db.query(related_data)`

**Search patterns:**
```
- for loop or forEach
- Inside loop: cursor.execute(), db.run(), db.query()
- Query depends on loop variable
```

**Example (Bad):**
```javascript
// AppManager.js
this.db.all("SELECT * FROM courses", [], (err, courses) => {
    courses.forEach(c => {
        // Inside forEach, query for each course
        this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
            // This runs once per course! N+1 problem
        });
    });
});
```

**Example (Good):**
```javascript
// courseController.js
async function getCourses() {
    // Single query with JOIN
    const courses = await db.query(`
        SELECT c.*, COUNT(e.id) as enrollment_count
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        GROUP BY c.id
    `);
    return courses;
}
```

**Recommendation:** Use JOINs, eager loading, or batch queries.

---

### 8. Code Duplication / DRY Violation

**Description:** Same code repeated in multiple locations without abstraction.

**Severity:** MEDIUM â€” Maintenance burden, inconsistency, bug propagation.

**Detection Signals:**
- Same validation logic in multiple controllers
- Same DB query patterns repeated
- Similar error handling blocks
- Identical response formatting

**Search patterns:**
```
- Function: validate_produto (validating product fields)
- Function: validate_usuario (validating user, same pattern)
- Function: criar_produto (building product response)
- Function: criar_usuario (building user response, similar structure)
```

**Example (Bad):**
```python
# controllers.py
def validate_produto(nome, preco, estoque):
    if not nome or len(nome) < 2: return False
    if preco < 0: return False
    if estoque < 0: return False
    return True

def validate_usuario(nome, email, senha):
    if not nome or len(nome) < 2: return False
    if not email or '@' not in email: return False
    if not senha or len(senha) < 6: return False
    return True

# And validation used in criar_produto, atualizar_produto, criar_usuario, etc.
```

**Example (Good):**
```python
# utils/validators.py
def validate_required_string(value, min_length=1, max_length=None):
    if not value or len(value) < min_length: return False
    if max_length and len(value) > max_length: return False
    return True

def validate_email(email):
    return '@' in email and '.' in email.split('@')[1]

# controllers/produto_controller.py
def criar_produto(data):
    if not validate_required_string(data['nome'], min_length=2): raise Error
    if data['preco'] < 0: raise Error
    ...
```

**Recommendation:** Extract common logic into utility functions or base classes.

---

### 9. Magic Numbers / Hardcoded Strings

**Description:** Hard-to-understand constants or configuration values scattered throughout code.

**Severity:** MEDIUM â€” Reduces maintainability, unclear intent.

**Detection Signals:**
- Numbers without context: `99999`, `3`, `30`
- String lists: `["admin", "user", "moderator"]`
- Status codes: `200`, `400`, `500`
- Repeated in multiple places

**Search patterns:**
```
- categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
- appears in multiple functions
- if status.startswith("4"): ...
- Various magic numbers without explanation
```

**Example (Bad):**
```python
# controllers.py
categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

if preco < 0: return error
if estoque < 0: return error
if len(nome) < 2: return error
if len(nome) > 200: return error

# And these same values repeated elsewhere
```

**Example (Good):**
```python
# config/constants.py
MIN_PRODUCT_NAME_LENGTH = 2
MAX_PRODUCT_NAME_LENGTH = 200
VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

# models/produto.py
if len(nome) < MIN_PRODUCT_NAME_LENGTH: raise ValidationError
```

**Recommendation:** Define constants in dedicated module, use enums for status values.

---

## LOW Severity

### 10. Unclear Variable Names

**Description:** Variable names that don't clearly indicate their purpose.

**Severity:** LOW â€” Reduces readability, increases onboarding time.

**Detection Signals:**
- Single letter variables: `u`, `e`, `p`, `c`, `d` (except in loops)
- Abbreviated unclear names: `usr`, `eml`, `pwd`, `cid`, `cc`
- Generic names: `data`, `result`, `temp`, `x`

**Search patterns:**
```
- let u = req.body.usr
- let e = req.body.eml
- let p = req.body.pwd
- let cid = req.body.c_id
- let cc = req.body.card
```

**Example (Bad):**
```javascript
// AppManager.js
app.post('/api/checkout', (req, res) => {
    let u = req.body.usr;
    let e = req.body.eml;
    let p = req.body.pwd;
    let cid = req.body.c_id;
    let cc = req.body.card;
    
    if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");
    // ...
});
```

**Example (Good):**
```javascript
// controllers/checkoutController.js
async function checkout(req, res) {
    const { username, email, password, courseId, cardNumber } = req.body;
    
    if (!username || !email || !courseId || !cardNumber) {
        return res.status(400).json({error: "Missing required fields"});
    }
    // ...
}
```

**Recommendation:** Use descriptive names: `username` instead of `u`, `email` instead of `e`.

---

### 11. Unnecessary Imports

**Description:** Import statements for modules that are not used in the file.

**Severity:** LOW â€” Reduces clarity, may impact startup time.

**Detection Signals:**
- `import os`, `import sys` not used
- `from unused_module import something`
- Can verify by checking if name appears in code below

**Search patterns:**
```
- import os  (not in file)
- import sys  (not in file)
- import json  (not in file)
- import time  (not in file)
```

**Example (Bad):**
```python
# routes/task_routes.py
import os      # Not used
import sys     # Not used
import json    # Not used
from datetime import datetime

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    # No use of os, sys, json
```

**Example (Good):**
```python
# routes/task_routes.py
from datetime import datetime

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()
    # Only imports what's needed
```

**Recommendation:** Remove unused imports, use linters like `pylint` or `eslint`.

---

## Detection Priority

When scanning a project, check in this order:

1. âœ… **CRITICAL** (blocks everything):
   - Hardcoded Credentials
   - SQL Injection
   - God Class

2. âœ… **HIGH** (breaks architecture):
   - Direct DB Access
   - Callback Hell
   - Global Mutable State

3. âœ… **MEDIUM** (reduces maintainability):
   - N+1 Queries
   - Code Duplication
   - Magic Numbers

4. âœ… **LOW** (quality improvements):
   - Unclear Names
   - Unnecessary Imports

---

## Summary

For each finding:
- Identify anti-pattern name
- Note severity (CRITICAL/HIGH/MEDIUM/LOW)
- Record exact file and line number(s)
- Describe the specific instance
- Note impact on the project
- Recommend the fix
- Reference transformation in playbook

Total minimum: 8 anti-patterns across all severities.

---

## LOW Severity

### 12. Deprecated APIs / Obsolete Framework Usage

**Description:** Uso de APIs obsoletas, métodos substituídos por alternativas modernas ou recursos marcados como deprecated pela linguagem/framework.

**Severity:** LOW a MEDIUM — Pode quebrar em upgrades, gerar warnings e dificultar manutenção. Elevar para MEDIUM quando afeta rotas, persistência ou segurança.

**Detection Signals:**
- Python/Flask/SQLAlchemy:
  - `Model.query.get(id)` em SQLAlchemy 2.x; preferir `db.session.get(Model, id)`
  - funções antigas de hashing como `hashlib.md5()` para senhas
  - imports não utilizados de APIs legadas
- Node.js/Express:
  - callbacks aninhados em APIs que já possuem Promise wrappers
  - pacotes ou métodos com warnings de depreciação no `npm install`
  - APIs antigas de criptografia ou hashing caseiro

**Search patterns:**
```
- SQLAlchemy: .query.get(
- Python security: hashlib.md5, base64 password hash
- Node.js: deprecated package warnings, custom callback wrappers without Promise abstraction
- Framework warnings during install/test
```

**Recommendation:** Substituir por API moderna suportada, registrar no relatório quando não houver ocorrência aplicável e validar com warnings de runtime/instalação.
