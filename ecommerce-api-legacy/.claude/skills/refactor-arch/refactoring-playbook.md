# Refactoring Playbook: Transformation Patterns

Complete guide with 8+ before/after examples for each anti-pattern.

---

## Pattern 1: Hardcoded Credentials → Environment Variables

### Problem
```python
# ❌ BAD: app.py
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
DB_PASSWORD = "root123"
API_KEY = "pk_live_1234567890"
```

### Solution
```python
# ✅ GOOD: config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    API_KEY = os.getenv('API_KEY')

config = Config()

# ✅ GOOD: app.py
from config.settings import config
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# ✅ GOOD: .env (git-ignored)
SECRET_KEY=minha-chave-super-secreta-123
DEBUG=False
DB_PASSWORD=root123
API_KEY=pk_live_1234567890

# ✅ GOOD: .env.example (committed)
SECRET_KEY=your_secret_key_here
DEBUG=False
DB_PASSWORD=your_db_password_here
API_KEY=your_api_key_here
```

### Node.js Version
```javascript
// ❌ BAD: utils.js
const config = {
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@fullcycle.com.br"
};

// ✅ GOOD: config/index.js
require('dotenv').config();

module.exports = {
    dbPass: process.env.DB_PASSWORD,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    smtpUser: process.env.SMTP_USER,
    port: process.env.PORT || 3000
};

// ✅ GOOD: .env
DB_PASSWORD=senha_super_secreta_prod_123
PAYMENT_GATEWAY_KEY=pk_live_1234567890abcdef
SMTP_USER=no-reply@fullcycle.com.br
PORT=3000
```

---

## Pattern 2: SQL Injection → Parameterized Queries

### Python Problem
```python
# ❌ BAD: models.py
def get_produto_por_id(id):
    cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
    row = cursor.fetchone()
    return row

def criar_produto(nome, descricao, preco):
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco) VALUES ('" +
        nome + "', '" + descricao + "', " + str(preco) + ")"
    )
```

### Python Solution
```python
# ✅ GOOD: models/produto_model.py
from config.database import get_db

class ProdutoModel:
    @staticmethod
    def get_produto_por_id(id):
        db = get_db()
        cursor = db.cursor()
        # Use ? for placeholders
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    @staticmethod
    def criar_produto(nome, descricao, preco):
        db = get_db()
        cursor = db.cursor()
        # Parameters as tuple
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco) VALUES (?, ?, ?)",
            (nome, descricao, preco)
        )
        db.commit()
        return cursor.lastrowid
```

### Node.js Problem
```javascript
// ❌ BAD: AppManager.js
this.db.get("SELECT * FROM courses WHERE id = " + id, (err, course) => {
    ...
});

this.db.run("INSERT INTO users VALUES (" + userId + ", '" + name + "', '" + email + "')", 
    (err) => { ... }
);
```

### Node.js Solution
```javascript
// ✅ GOOD: models/courseModel.js
class CourseModel {
    static async getCourseById(id) {
        return new Promise((resolve, reject) => {
            // Use ? for placeholders
            db.get("SELECT * FROM courses WHERE id = ?", [id], (err, course) => {
                if (err) reject(err);
                else resolve(course);
            });
        });
    }
    
    static async createUser(userId, name, email) {
        return new Promise((resolve, reject) => {
            // Parameters in array
            db.run("INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
                [userId, name, email],
                function(err) {
                    if (err) reject(err);
                    else resolve(this.lastID);
                }
            );
        });
    }
}

module.exports = CourseModel;
```

---

## Pattern 3: God Class → Separate Models/Controllers/Views

### Problem
```python
# ❌ BAD: Single app.py with everything
class App:
    def __init__(self):
        self.db = sqlite3.connect(':memory:')
    
    def setup_routes(self, app):
        # Routes defined here
        @app.post('/checkout')
        def checkout():
            # Validation here
            # DB queries here
            # Business logic here
            # Response formatting here
            # Audit logging here
            ...
```

### Solution
```python
# ✅ GOOD: config/database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# ✅ GOOD: models/user.py
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

# ✅ GOOD: models/course.py
class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)

# ✅ GOOD: controllers/checkout_controller.py
class CheckoutController:
    @staticmethod
    def process_checkout(user_data, course_id):
        # Find or create user
        user = User.query.filter_by(email=user_data['email']).first()
        if not user:
            user = User(
                name=user_data['name'],
                email=user_data['email']
            )
            db.session.add(user)
            db.session.commit()
        
        # Get course
        course = Course.query.get(course_id)
        if not course:
            raise ValueError("Course not found")
        
        # Create enrollment
        enrollment = Enrollment(user_id=user.id, course_id=course_id)
        db.session.add(enrollment)
        db.session.commit()
        
        # Log audit
        audit_log = AuditLog(
            action=f"Checkout course {course_id} by user {user.id}"
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return {
            'success': True,
            'enrollment_id': enrollment.id,
            'message': 'Enrollment successful'
        }

# ✅ GOOD: views/checkout_routes.py
from flask import Blueprint, request, jsonify
from controllers.checkout_controller import CheckoutController

checkout_bp = Blueprint('checkout', __name__)

@checkout_bp.route('/checkout', methods=['POST'])
def checkout():
    try:
        data = request.get_json()
        result = CheckoutController.process_checkout(
            user_data={'name': data['name'], 'email': data['email']},
            course_id=data['course_id']
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ✅ GOOD: app.py
from flask import Flask
from flask_cors import CORS
from config.database import db
from views.checkout_routes import checkout_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

CORS(app)
db.init_app(app)

app.register_blueprint(checkout_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
```

---

## Pattern 4: Direct DB Access → Repository Pattern

### Problem
```python
# ❌ BAD: Each controller has its own DB logic
def crear_produto():  # in controllers.py
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO produtos ...")
    db.commit()

def atualizar_produto():  # in controllers.py
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE produtos ...")
    db.commit()
```

### Solution
```python
# ✅ GOOD: models/repositories/product_repository.py
class ProductRepository:
    def __init__(self, db):
        self.db = db
    
    def find_all(self):
        return Product.query.all()
    
    def find_by_id(self, id):
        return Product.query.get(id)
    
    def create(self, data):
        produto = Product(**data)
        self.db.session.add(produto)
        self.db.session.commit()
        return produto
    
    def update(self, id, data):
        produto = Product.query.get(id)
        if not produto:
            raise ValueError("Produto não encontrado")
        for key, value in data.items():
            setattr(produto, key, value)
        self.db.session.commit()
        return produto
    
    def delete(self, id):
        produto = Product.query.get(id)
        if produto:
            self.db.session.delete(produto)
            self.db.session.commit()
            return True
        return False

# ✅ GOOD: controllers/product_controller.py
from models.repositories.product_repository import ProductRepository

class ProductController:
    def __init__(self, product_repo: ProductRepository):
        self.repo = product_repo
    
    def criar_produto(self, data):
        try:
            produto = self.repo.create(data)
            return {'success': True, 'data': produto.to_dict()}, 201
        except Exception as e:
            return {'error': str(e)}, 500
    
    def atualizar_produto(self, id, data):
        try:
            produto = self.repo.update(id, data)
            return {'success': True, 'data': produto.to_dict()}, 200
        except Exception as e:
            return {'error': str(e)}, 400
```

---

## Pattern 5: Callback Hell → Async/Await

### Problem
```javascript
// ❌ BAD: Deeply nested callbacks
app.post('/checkout', (req, res) => {
    const userId = req.body.usr;
    
    db.get("SELECT * FROM courses WHERE id = ?", [courseId], (err, course) => {
        if (err) return res.status(500).send("Error");
        
        db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
            if (err) return res.status(500).send("Error");
            
            if (!user) {
                db.run("INSERT INTO users VALUES (...)", (err) => {
                    if (err) return res.status(500).send("Error");
                    
                    db.run("INSERT INTO enrollments ...", (err) => {
                        if (err) return res.status(500).send("Error");
                        res.json({success: true});
                    });
                });
            } else {
                db.run("INSERT INTO enrollments ...", (err) => {
                    if (err) return res.status(500).send("Error");
                    res.json({success: true});
                });
            }
        });
    });
});
```

### Solution
```javascript
// ✅ GOOD: Using async/await
app.post('/checkout', async (req, res, next) => {
    try {
        const { email, courseId } = req.body;
        
        // Get course
        const course = await getCourseAsync(courseId);
        if (!course) {
            return res.status(404).json({error: 'Course not found'});
        }
        
        // Find or create user
        let user = await getUserByEmailAsync(email);
        if (!user) {
            user = await createUserAsync({email});
        }
        
        // Create enrollment
        const enrollment = await createEnrollmentAsync({
            userId: user.id,
            courseId: course.id
        });
        
        // Log audit
        await logAuditAsync(`Checkout course ${courseId} by user ${user.id}`);
        
        res.json({
            success: true,
            enrollmentId: enrollment.id
        });
    } catch (error) {
        next(error);
    }
});

// Helper functions using Promises
function getCourseAsync(id) {
    return new Promise((resolve, reject) => {
        db.get("SELECT * FROM courses WHERE id = ?", [id], (err, course) => {
            if (err) reject(err);
            else resolve(course);
        });
    });
}

function getUserByEmailAsync(email) {
    return new Promise((resolve, reject) => {
        db.get("SELECT * FROM users WHERE email = ?", [email], (err, user) => {
            if (err) reject(err);
            else resolve(user);
        });
    });
}

// Or using Sequelize ORM
async function checkoutWithORM(req, res, next) {
    try {
        const course = await Course.findByPk(req.body.courseId);
        const user = await User.findOrCreate({
            where: {email: req.body.email},
            defaults: {name: req.body.name}
        });
        
        const enrollment = await Enrollment.create({
            userId: user.id,
            courseId: course.id
        });
        
        res.json({success: true, enrollmentId: enrollment.id});
    } catch (error) {
        next(error);
    }
}
```

---

## Pattern 6: Global Mutable State → Singleton/Dependency Injection

### Problem
```javascript
// ❌ BAD: Global mutable variables
let globalCache = {};
let totalRevenue = 0;

function logAndCache(key, data) {
    globalCache[key] = data;  // Mutation
}

module.exports = { globalCache, totalRevenue };
```

### Solution
```javascript
// ✅ GOOD: Encapsulated service
class CacheService {
    constructor() {
        this.cache = {};
    }
    
    set(key, value) {
        this.cache[key] = value;
    }
    
    get(key) {
        return this.cache[key];
    }
    
    clear() {
        this.cache = {};
    }
}

class RevenueService {
    constructor() {
        this.total = 0;
    }
    
    add(amount) {
        this.total += amount;
    }
    
    getTotal() {
        return this.total;
    }
}

// ✅ GOOD: Usage with dependency injection
class CheckoutController {
    constructor(cacheService, revenueService) {
        this.cache = cacheService;
        this.revenue = revenueService;
    }
    
    async processCheckout(data) {
        const enrollment = await this.createEnrollment(data);
        
        this.cache.set(`checkout_${data.userId}`, {
            enrollmentId: enrollment.id,
            timestamp: new Date()
        });
        
        this.revenue.add(data.amount);
        
        return {success: true, enrollmentId: enrollment.id};
    }
}

// ✅ GOOD: Dependency injection in app setup
const cacheService = new CacheService();
const revenueService = new RevenueService();
const checkoutController = new CheckoutController(cacheService, revenueService);

app.post('/checkout', (req, res) => {
    checkoutController.processCheckout(req.body)
        .then(result => res.json(result))
        .catch(err => res.status(500).json({error: err.message}));
});
```

---

## Pattern 7: N+1 Queries → JOIN + Eager Loading

### Problem
```javascript
// ❌ BAD: Loop with inner query (N+1)
async function getCoursesWithEnrollments() {
    const courses = await db.all("SELECT * FROM courses");  // 1 query
    
    for (const course of courses) {
        // This executes N times!
        const enrollments = await db.all(
            "SELECT * FROM enrollments WHERE course_id = ?",
            [course.id]
        );
        course.enrollments = enrollments;
    }
    
    return courses;  // 1 + N queries total!
}
```

### Solution
```javascript
// ✅ GOOD: Use JOIN
async function getCoursesWithEnrollments() {
    const data = await db.all(`
        SELECT c.*, 
               COUNT(e.id) as enrollment_count,
               json_group_array(json_object(
                   'id', e.id,
                   'user_id', e.user_id
               )) as enrollments
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        GROUP BY c.id
    `);
    
    return data;  // Just 1 query!
}

// ✅ GOOD: Using ORM with eager loading
async function getCoursesWithEnrollments() {
    const courses = await Course.findAll({
        include: [{
            model: Enrollment,
            attributes: ['id', 'user_id'],
            through: {attributes: []} // if many-to-many
        }],
        raw: true
    });
    
    return courses;
}
```

---

## Pattern 8: Code Duplication → Extract Functions

### Problem
```python
# ❌ BAD: Same validation repeated
def criar_produto():
    if not nome or len(nome) < 2: return error
    if preco < 0: return error
    if estoque < 0: return error
    ...

def atualizar_produto():
    if not nome or len(nome) < 2: return error
    if preco < 0: return error
    if estoque < 0: return error
    ...

def criar_usuario():
    if not nome or len(nome) < 2: return error
    if not email or '@' not in email: return error
    ...
```

### Solution
```python
# ✅ GOOD: Centralized validators
# utils/validators.py
def validate_name(name, min_length=2, max_length=200):
    if not name or len(name) < min_length:
        return "Name too short"
    if len(name) > max_length:
        return "Name too long"
    return None

def validate_price(price):
    if price < 0:
        return "Price must be positive"
    return None

def validate_stock(stock):
    if stock < 0:
        return "Stock must be positive"
    return None

def validate_email(email):
    if '@' not in email or '.' not in email.split('@')[1]:
        return "Invalid email"
    return None

# Usage in controllers
# controllers/product_controller.py
def criar_produto(data):
    errors = {}
    
    if error := validate_name(data.get('nome')):
        errors['nome'] = error
    if error := validate_price(data.get('preco')):
        errors['preco'] = error
    if error := validate_stock(data.get('estoque')):
        errors['estoque'] = error
    
    if errors:
        return {'errors': errors}, 400
    
    # Create product
    produto = Produto.create(data)
    return {'success': True, 'data': produto.to_dict()}, 201

# controllers/user_controller.py
def criar_usuario(data):
    errors = {}
    
    if error := validate_name(data.get('nome')):
        errors['nome'] = error
    if error := validate_email(data.get('email')):
        errors['email'] = error
    
    if errors:
        return {'errors': errors}, 400
    
    # Create user
    usuario = Usuario.create(data)
    return {'success': True, 'data': usuario.to_dict()}, 201
```

---

## Pattern 9: Magic Numbers/Strings → Constants

### Problem
```python
# ❌ BAD: Hardcoded values scattered
def criar_produto():
    if len(nome) < 2: error()  # What's 2?
    if len(nome) > 200: error()  # What's 200?
    if preco < 0: error()
    if estoque < 0: error()
    categorias = ["informatica", "moveis", "vestuario", "geral"]  # Lists repeated
    if categoria not in categorias: error()

def atualizar_status_pedido():
    if status not in ["pendente", "processando", "enviado", "entregue"]: error()  # List repeated
```

### Solution
```python
# ✅ GOOD: Centralized constants
# config/constants.py
# Product constants
MIN_PRODUCT_NAME_LENGTH = 2
MAX_PRODUCT_NAME_LENGTH = 200
VALID_PRODUCT_CATEGORIES = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros"
]

# Order status constants
class OrderStatus:
    PENDING = "pendente"
    PROCESSING = "processando"
    SENT = "enviado"
    DELIVERED = "entregue"
    CANCELLED = "cancelado"
    
    ALL = [PENDING, PROCESSING, SENT, DELIVERED, CANCELLED]

# Usage
# controllers/product_controller.py
from config.constants import (
    MIN_PRODUCT_NAME_LENGTH,
    MAX_PRODUCT_NAME_LENGTH,
    VALID_PRODUCT_CATEGORIES
)

def criar_produto(data):
    if len(data['nome']) < MIN_PRODUCT_NAME_LENGTH:
        return {'error': 'Name too short'}, 400
    if len(data['nome']) > MAX_PRODUCT_NAME_LENGTH:
        return {'error': 'Name too long'}, 400
    if data['categoria'] not in VALID_PRODUCT_CATEGORIES:
        return {'error': 'Invalid category'}, 400

# controllers/order_controller.py
from config.constants import OrderStatus

def atualizar_status_pedido(pedido_id, novo_status):
    if novo_status not in OrderStatus.ALL:
        return {'error': 'Invalid status'}, 400
```

---

## Pattern 10: Unclear Variable Names → Descriptive Names

### Problem
```javascript
// ❌ BAD: Cryptic names
app.post('/api/checkout', (req, res) => {
    let u = req.body.usr;
    let e = req.body.eml;
    let p = req.body.pwd;
    let cid = req.body.c_id;
    let cc = req.body.card;
    
    if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");
    
    console.log(`Processing card ${cc} for user ${u}`);
    // ...
});
```

### Solution
```javascript
// ✅ GOOD: Clear, descriptive names
app.post('/api/checkout', async (req, res, next) => {
    const { username, email, password, courseId, cardNumber } = req.body;
    
    // Validate required fields
    if (!username || !email || !courseId || !cardNumber) {
        return res.status(400).json({
            error: "Missing required fields: username, email, courseId, cardNumber"
        });
    }
    
    try {
        const checkoutResult = await processCheckout({
            username,
            email,
            password,
            courseId,
            cardNumber
        });
        
        console.log(`Processing card ending in ${cardNumber.slice(-4)} for user ${username}`);
        res.json({success: true, ...checkoutResult});
    } catch (error) {
        next(error);
    }
});
```

---

## Transformation Checklist

When refactoring, ensure:

- ✅ All hardcoded secrets extracted to env vars
- ✅ All SQL queries use parameterized statements (? or $1)
- ✅ God classes split into separate models, controllers, views
- ✅ DB access isolated in repository/model layer
- ✅ Callbacks converted to async/await
- ✅ Global mutable state replaced with services
- ✅ N+1 queries fixed with JOINs
- ✅ Duplicated code extracted to functions
- ✅ Magic numbers/strings converted to constants
- ✅ Variable names clarified
- ✅ Unnecessary imports removed

---

## Summary

| Anti-Pattern | Transformation | Key Benefit |
|:---|:---|:---|
| Hardcoded Secrets | → Environment Variables | Security |
| SQL Injection | → Parameterized Queries | Security |
| God Class | → M/C/V Separation | Testability |
| Direct DB Access | → Repository Pattern | Flexibility |
| Callback Hell | → Async/Await | Readability |
| Global State | → Dependency Injection | Concurrency |
| N+1 Queries | → JOINs + Eager Load | Performance |
| Duplicated Code | → Extracted Functions | Maintainability |
| Magic Numbers | → Named Constants | Clarity |
| Cryptic Names | → Descriptive Names | Readability |

Each transformation follows the same principle: **separate concerns, make dependencies explicit, extract complexity**.

---

## Transformation 9: Deprecated APIs ? Modern Supported APIs

### Problem
APIs obsoletas geram warnings, dificultam upgrades e podem ser removidas em vers�es futuras.

### Python / SQLAlchemy Example
**Before:**
```python
user = User.query.get(user_id)
```

**After:**
```python
user = db.session.get(User, user_id)
```

### Security Example
**Before:**
```python
password_hash = hashlib.md5(password.encode()).hexdigest()
```

**After:**
```python
password_hash = generate_password_hash(password)
```

### Node.js Example
**Before:** callback direto espalhado nas rotas.
```javascript
db.get(sql, params, (err, row) => { ... })
```

**After:** adapter Promise centralizado.
```javascript
const row = await dbGet(sql, params)
```

### Validation
- Rodar testes/smoke tests ap�s troca.
- Verificar aus�ncia de warnings relevantes quando poss�vel.
- Garantir compatibilidade dos endpoints existentes.
