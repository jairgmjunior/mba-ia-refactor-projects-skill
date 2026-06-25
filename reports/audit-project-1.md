================================
ARCHITECTURE AUDIT REPORT
================================

**Project:** code-smells-project  
**Stack:** Python 3.x + Flask 3.1.1  
**Database:** SQLite  
**Domain:** E-commerce API (products, users, orders)  
**Files Analyzed:** 4 source files  
**Approx. Lines of Code:** ~800

---

## Executive Summary

| Severity | Count |
|:---:|:---:|
| CRITICAL | 3 |
| HIGH | 2 |
| MEDIUM | 2 |
| LOW | 1 |
| **TOTAL** | **8** |

**Overall Assessment:** Project exhibits critical architecture violations with hardcoded credentials, SQL injection vulnerabilities, and god class pattern. High risk of security breach and complete lack of testability.

---

## Detailed Findings

### [CRITICAL] Hardcoded Credentials & Debug Mode

**File:** app.py:8-9  
**Description:** SECRET_KEY hardcoded as 'minha-chave-super-secreta-123' and DEBUG=True in code.  
**Impact:** If code is compromised or pushed to public repo, attacker can forge sessions. DEBUG mode exposes stack traces with sensitive info.  
**Recommendation:** Extract to environment variables using python-dotenv. Use .env file (git-ignored).  

**Current Code:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

**Refactored Code:**
```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()
app.config["SECRET_KEY"] = os.getenv('SECRET_KEY')
app.config["DEBUG"] = os.getenv('DEBUG', 'False') == 'True'

# .env (git-ignored)
SECRET_KEY=minha-chave-super-secreta-123
DEBUG=False
```

---

### [CRITICAL] SQL Injection Vulnerabilities

**File:** models.py:28-35  
**Description:** Database queries built using string concatenation instead of parameterized queries. Lines affected:
- Line 28: `cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))`
- Line 36-40: `"INSERT INTO produtos (nome, descricao, preco, ...) VALUES ('" + nome + ...`
- Line 85: `cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`

**Impact:** Attacker can inject malicious SQL code to bypass authentication, steal data, or delete entire database.  
**Recommendation:** Use parameterized queries with ? placeholders. Alternatively, use SQLAlchemy ORM.

**Current Code (Bad):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute("INSERT INTO produtos (...) VALUES ('" + nome + "', '" + descricao + "', ...)")
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
```

**Refactored Code (Good):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("INSERT INTO produtos (...) VALUES (?, ?, ?)", (nome, descricao, preco))
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
```

---

### [CRITICAL] God Class Pattern

**File:** app.py:1-89  
**Description:** Single file contains all application concerns:
- Routes definition (lines 12-30)
- Health check endpoint (line 29)
- Admin reset-db endpoint without authentication (lines 32-40)
- Admin query execution endpoint without authentication (lines 42-56)
- Entry point initialization (lines 58-89)

All of these mixed responsibilities make testing impossible and any change affects entire application.

**Impact:** 
- Impossible to unit test individual features
- Cannot reuse validation logic
- Single point of failure
- Violates Single Responsibility Principle

**Recommendation:** Separate into models/controllers/views following MVC pattern.

**Current Structure (Bad):**
```
app.py
├── Flask config
├── Routes definition
├── Health check
├── Admin endpoints
└── Entry point
```

**Refactored Structure (Good):**
```
src/
├── config/
│   ├── settings.py
│   └── database.py
├── models/
│   └── [entity models]
├── controllers/
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── views/
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   └── pedido_routes.py
├── middleware/
│   └── error_handler.py
└── app.py
```

---

### [HIGH] Acesso Direto ao Banco de Dados sem Abstração

**File:** controllers.py:1-100  
**Description:** Controllers directly execute SQL queries using cursor.execute() without using a data access layer or ORM.

**Impact:** 
- DB logic scattered across application
- Hard to change database
- Cannot mock DB for unit tests
- Difficult to implement caching

**Recommendation:** Create Model/Repository layer that encapsulates DB operations.

**Current Code (Bad):**
```python
# controllers.py
def criar_produto():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos ...")  # ← Direct DB access
    db.commit()
```

**Refactored Code (Good):**
```python
# models/produto_model.py
class Produto(db.Model):
    @staticmethod
    def create(nome, preco, estoque):
        # ← Encapsulates DB operation
        produto = Produto(nome=nome, preco=preco, estoque=estoque)
        db.session.add(produto)
        db.session.commit()
        return produto

# controllers/produto_controller.py
def criar_produto(data):
    produto = Produto.create(...)  # ← Uses model
    return {'success': True, 'data': produto.to_dict()}
```

---

### [HIGH] Falta de Separação de Responsabilidades

**File:** controllers.py:1-100  
**Description:** Controllers mix validation, DB access, and HTTP response formatting:
- Lines 20-30: Input validation
- Lines 32-45: DB queries
- Lines 47-50: Response formatting

All in same function without abstraction.

**Impact:** 
- Cannot reuse validation in other contexts
- Hard to unit test (must mock DB + HTTP)
- Difficult to maintain

**Recommendation:** Extract validation into utils/validators.py. Use models for DB. Controllers should orchestrate only.

**Current Code (Bad):**
```python
def criar_produto():
    dados = request.get_json()
    
    # Validation mixed with business logic
    if not dados.get("nome"):
        return jsonify({"erro": "Nome obrigatório"}), 400
    if dados["preco"] < 0:
        return jsonify({"erro": "Preço negativo"}), 400
    
    # DB access in controller
    models.criar_produto(dados["nome"], dados["preco"])
    
    # Response formatting
    return jsonify({"mensagem": "Sucesso"}), 201
```

**Refactored Code (Good):**
```python
# utils/validators.py
def validar_produto(dados):
    erros = {}
    if not dados.get("nome"):
        erros["nome"] = "Nome obrigatório"
    if dados.get("preco", -1) < 0:
        erros["preco"] = "Preço deve ser positivo"
    return erros

# controllers/produto_controller.py
def criar_produto(dados):
    erros = validar_produto(dados)
    if erros:
        return {"erro": erros}, 400
    
    produto = Produto.create(**dados)
    return {"mensagem": "Sucesso", "data": produto.to_dict()}, 201

# views/produto_routes.py
@bp.route('/produtos', methods=['POST'])
def criar_produto_route():
    dados = request.get_json()
    result, status = ProdutoController.criar_produto(dados)
    return jsonify(result), status
```

---

### [MEDIUM] Duplicação de Validação

**File:** controllers.py (multiple functions)  
**Description:** Same validation rules repeated in create and update functions:
- Product name validation (min 2, max 200 chars)
- Price validation (must be ≥ 0)
- Stock validation (must be ≥ 0)
- Category validation (must be in allowed list)

**Impact:** If validation logic changes, must update multiple places. Risk of inconsistency.

**Recommendation:** Extract to reusable validation functions in utils/validators.py.

---

### [MEDIUM] Magic Strings Hardcoded

**File:** controllers.py:45-60  
**Description:** Category list hardcoded in multiple functions:
```python
categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
```
This same list appears in criar_produto, atualizar_produto, and elsewhere.

**Impact:** No single source of truth. If categories change, must update multiple places.

**Recommendation:** Move to config/constants.py.

**Current Code (Bad):**
```python
def criar_produto():
    categorias_validas = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
    if categoria not in categorias_validas:
        return error
```

**Refactored Code (Good):**
```python
# config/constants.py
VALID_PRODUCT_CATEGORIES = [
    "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"
]

# controllers/produto_controller.py
from config.constants import VALID_PRODUCT_CATEGORIES
if categoria not in VALID_PRODUCT_CATEGORIES:
    return error
```

---

### [LOW] Importação Desnecessária

**File:** models.py:2  
**Description:** `import sqlite3` is imported but never used. Database connection is managed through database.py's get_db() function.

**Impact:** Adds confusion about dependencies. Potential unused import could slow module load.

**Recommendation:** Remove unused import.

---

## Refactoring Recommendations

### Priority 1: Address CRITICAL Issues (Must Do)
1. **Extract Secrets to Environment Variables** — Risk of credential compromise
2. **Fix SQL Injection** — Risk of database breach
3. **Separate Concerns (God Class)** — Affects testability and maintainability

### Priority 2: Address HIGH Issues (Should Do)
1. **Create Model Layer** — Abstraction for DB operations
2. **Extract Validation** — Reusable validation logic

### Priority 3: Address MEDIUM Issues (Could Do)
1. **Centralize Constants** — Single source of truth
2. **Eliminate Duplication** — Easier maintenance

### Priority 4: Address LOW Issues (Nice-to-Have)
1. **Remove Unused Imports** — Cleaner code

---

## Target Architecture

### Current (Monolithic)
```
app.py (89 lines) — Everything here
├── Flask config
├── Routes
├── Health checks
├── Admin endpoints
└── Entry point

models.py (150 lines) — All DB logic
controllers.py (100 lines) — Validation + biz logic
database.py — DB connection
```

### Target (MVC)
```
src/
├── config/
│   ├── settings.py (env vars, config)
│   ├── database.py (DB connection)
│   └── constants.py (magic values)
├── models/
│   ├── base_model.py (if using ORM)
│   ├── produto.py
│   ├── usuario.py
│   └── pedido.py
├── controllers/
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── views/
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   └── pedido_routes.py
├── middleware/
│   └── error_handler.py
├── utils/
│   ├── validators.py
│   └── helpers.py
├── app.py (app creation)
└── main.py (entry point)
```

---

## Validation Checklist (Post-Refactor)

- [ ] Application starts without errors
- [ ] All endpoints respond with same API contract
- [ ] Database initializes properly
- [ ] No hardcoded secrets in code
- [ ] SQL queries use parameterized statements
- [ ] Clear separation of concerns (M/C/V)
- [ ] Error handling centralized
- [ ] Duplicate code eliminated
- [ ] Magic numbers/strings extracted to constants
- [ ] Variable names clarified
- [ ] Unnecessary imports removed

---

## Estimated Effort

| Task | Effort | Priority |
|:---|:---:|:---:|
| Extract secrets | 1 hour | MUST |
| Fix SQL Injection | 2 hours | MUST |
| Separate into MVC | 4 hours | MUST |
| Create Model/Repository | 2 hours | SHOULD |
| Extract validation | 1 hour | SHOULD |
| Centralize constants | 1 hour | COULD |
| **Total** | **11 hours** | - |

---

## Next Steps

1. **Review** this audit report
2. **Confirm** you want to proceed with refactoring
3. **Execute** Phase 3 (Refactoring):
   - Create config module with env vars
   - Convert models to use ORM or repository pattern
   - Extract validation to utils
   - Separate routes into views
   - Create controllers for orchestration
   - Add middleware for error handling
4. **Validate** result:
   - Application starts
   - All endpoints respond
   - Database works
   - 0 CRITICAL findings remaining
5. **Test** thoroughly before deployment

---

**Generated:** 2026-06-06  
**Project:** code-smells-project  
**Analyst:** Architectural Audit Skill  
**Severity Distribution:** 3 CRITICAL (37.5%) | 2 HIGH (25%) | 2 MEDIUM (25%) | 1 LOW (12.5%)
