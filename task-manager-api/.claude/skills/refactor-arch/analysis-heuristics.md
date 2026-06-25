# Analysis Heuristics: Detecting Language, Framework, and Architecture

## Language Detection

### Python
**Signals:**
- File extensions: `.py`
- Common imports: `import flask`, `import django`, `import fastapi`, `from flask import`, `from django import`
- Dependency files: `requirements.txt`, `Pipfile`, `pyproject.toml`
- Characteristics: indentation-based syntax, `def`, `class`, `import`

**Detection pattern:**
```
IF exists(*.py) AND exists(requirements.txt OR Pipfile) → Language = Python
```

### Node.js / JavaScript
**Signals:**
- File extensions: `.js`, `.ts`
- Common imports: `const express = require()`, `import express from`, `require('express')`
- Dependency files: `package.json`
- Characteristics: `function`, `const`, `require()`, `export`

**Detection pattern:**
```
IF exists(*.js) AND exists(package.json) → Language = Node.js/JavaScript
IF exists(*.ts) AND exists(package.json) → Language = TypeScript
```

---

## Framework Detection

### Python Frameworks

#### Flask
**Signals:**
- Import: `from flask import Flask`, `import flask`
- File structure: `app.py`, `application.py`
- Patterns: `@app.route()`, `Flask(__name__)`
- Dependencies: `flask`, `flask-sqlalchemy`, `flask-cors`

**Confirmation:**
```python
from flask import Flask
app = Flask(__name__)
```

#### Django
**Signals:**
- Import: `from django.conf`, `import django`
- File structure: `manage.py`, `settings.py`, `urls.py`
- Patterns: `django.db`, `@csrf_exempt`
- Dependencies: `django`, `djangorestframework`

#### FastAPI
**Signals:**
- Import: `from fastapi import FastAPI`
- Patterns: `@app.get()`, `@app.post()`, `FastAPI()`
- Dependencies: `fastapi`, `uvicorn`

### Node.js Frameworks

#### Express
**Signals:**
- Import: `const express = require('express')`, `import express from 'express'`
- Patterns: `app.get()`, `app.post()`, `express.Router()`
- Dependencies: `express` in package.json
- Files: `app.js`, `server.js`

#### NestJS
**Signals:**
- Import: `import { Module }`, `import { Controller }`
- Patterns: `@Module()`, `@Controller()`, `@Get()`, `@Post()`
- Dependencies: `@nestjs/core`, `@nestjs/common`
- File structure: `*.module.ts`, `*.controller.ts`

#### Koa
**Signals:**
- Import: `const Koa = require('koa')`
- Patterns: `ctx.body`, `router.get()`, `app.use()`
- Dependencies: `koa`, `koa-router`

---

## Database Detection

### SQLite
**Signals:**
- Python: `import sqlite3`, `from flask_sqlalchemy import SQLAlchemy`, `sqlite:///`
- Node.js: `const sqlite3 = require('sqlite3')`, `require('better-sqlite3')`
- Files: `.db`, `.sqlite`, `*.sqlite3`
- Connection string pattern: `:memory:` or file path

### PostgreSQL
**Signals:**
- Python: `import psycopg2`, `postgresql://`, `pg_connection`
- Node.js: `pg`, `node-postgres`
- Connection string pattern: `postgresql://user:pass@host:5432/db`

### MongoDB
**Signals:**
- Python: `import pymongo`, `MongoClient`
- Node.js: `mongodb`, `mongoose`
- Connection string pattern: `mongodb://` or `mongodb+srv://`

### MySQL
**Signals:**
- Python: `import mysql.connector`, `MySQLdb`, `PyMySQL`
- Node.js: `mysql`, `mysql2`
- Connection string pattern: `mysql://`

---

## Architecture Detection

### Monolithic
**Signals:**
- Few files (< 5) at root level
- No clear separation of concerns
- All routes in one file
- All models in one file
- Mixed responsibilities (routing, business logic, DB queries in same file)
- Typically: `app.py` + `models.py` + `controllers.py` + `database.py`

### Partially Modular
**Signals:**
- Some separation: `routes/`, `models/`, `controllers/`
- But unclear responsibilities
- Some duplication across modules
- Missing or unclear config separation

### Modular (MVC-like)
**Signals:**
- Clear directories: `models/`, `controllers/`, `views/`, `routes/`
- Separated concerns
- Config in dedicated module
- Middleware layer
- Error handling centralized

---

## Pattern Detection Examples

### Python/Flask Monolith
```
├── app.py              ← Routes, config, entry point all mixed
├── models.py           ← Entities and DB queries
├── controllers.py      ← Business logic and validations
├── database.py         ← DB connection
├── requirements.txt
└── README.md
```

**Diagnosis:** Monolithic, no clear MVC separation

---

### Node.js/Express God Class
```
├── src/
│   ├── app.js          ← Routes defined here
│   ├── AppManager.js   ← Contains DB, routes setup, business logic, payments
│   ├── utils.js        ← Config + utility functions (no separation)
│   └── package.json
└── README.md
```

**Diagnosis:** God Class pattern, high coupling

---

### Python/Flask Partial MVC
```
├── app.py              ← Entry point, some config
├── database.py         ← DB connection
├── models/
│   ├── __init__.py
│   ├── task.py         ← Task entity
│   ├── user.py
│   └── category.py
├── routes/
│   ├── __init__.py
│   ├── task_routes.py  ← Task routes + serialization logic
│   ├── user_routes.py
│   └── report_routes.py
├── services/
│   ├── __init__.py
│   └── notification_service.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── requirements.txt
└── README.md
```

**Diagnosis:** Partially modular. Models are correct, but routes contain serialization logic (should be in controllers). Missing config module. Services present but unclear usage.

---

## MVC Pattern Target

### Expected Structure
```
src/
├── config/
│   ├── __init__.py      (or .js)
│   ├── settings.py      # Configuration, environment variables
│   └── database.py      # DB connection setup
├── models/
│   ├── __init__.py
│   ├── base_model.py    # Base class for ORM models
│   ├── entity1.py       # Entity definitions only
│   └── entity2.py
├── controllers/
│   ├── __init__.py
│   ├── entity1_controller.py  # Business logic, validations
│   └── entity2_controller.py
├── views/ (or routes/)
│   ├── __init__.py
│   ├── entity1_routes.py      # HTTP routes only
│   └── entity2_routes.py
├── middleware/
│   ├── __init__.py
│   ├── error_handler.py       # Centralized error handling
│   ├── auth.py                # Authentication
│   └── logging.py             # Logging
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   ├── helpers.py
│   └── decorators.py
├── __init__.py
├── app.py               # Composition root, app creation
└── main.py              # Entry point (if different from app.py)
```

### Responsibility Distribution

**Config:**
- Database connection setup
- Environment variables
- API keys, secrets (from env, not hardcoded)
- Server configuration

**Models:**
- Entity definitions (fields, types)
- Relationships
- Data validation methods
- Serialization methods (to_dict, to_json)

**Controllers:**
- Business logic
- Orchestration of operations
- Input validation
- Error handling logic

**Views/Routes:**
- HTTP endpoints definitions
- Request/response handling only
- Call to controllers
- No business logic

**Middleware:**
- Request/response interception
- Error handling
- Authentication
- CORS, logging, etc.

**Utils:**
- Shared utilities
- Constants
- Helper functions
- Validators

---

## Domain Identification

### Signals
- Database table names: `produtos`, `usuarios`, `pedidos` → E-commerce
- Endpoint patterns: `/tasks`, `/users`, `/categories` → Task Manager
- Authorization patterns: `/admin/`, `/api/user/` → Content Management
- Financial patterns: `/checkout`, `/payments`, `/invoices` → E-commerce/Payment System

### Examples
- **E-commerce**: Tables like products, users, orders, payments
- **Task Manager**: Tables like tasks, users, categories, tags
- **LMS**: Tables like courses, users, enrollments, payments
- **CMS**: Tables like posts, categories, users, comments

---

## Summary

When analyzing a project:
1. ✅ Detect language (extensions, imports, dependency files)
2. ✅ Detect framework (specific imports, project structure)
3. ✅ Detect database (connection strings, imports)
4. ✅ Identify architecture level (monolithic, partial, modular)
5. ✅ Determine domain (tables, endpoints, business context)
6. ✅ Count files and estimate complexity
7. ✅ Output Phase 1 summary
