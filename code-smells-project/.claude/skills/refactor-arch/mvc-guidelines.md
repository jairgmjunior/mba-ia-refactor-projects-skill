# MVC Guidelines: Target Architecture Pattern

Reference document for the target MVC architecture that refactored projects should follow.

---

## MVC Pattern Overview

**M - Model:** Encapsulates data and business rules  
**V - View:** Presents data to user (HTTP responses)  
**C - Controller:** Handles user input and orchestrates Model/View

---

## Directory Structure

### Python/Flask Target

```
project-name/
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py        # Configuration, env vars
│   │   ├── database.py        # DB connection setup
│   │   └── constants.py       # Constants, enums
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py      # Base model class (if using ORM)
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   └── ...
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py     # Business logic for users
│   │   ├── product_controller.py  # Business logic for products
│   │   ├── order_controller.py
│   │   └── ...
│   │
│   ├── views/ (or routes/)
│   │   ├── __init__.py
│   │   ├── user_routes.py         # HTTP endpoints for users
│   │   ├── product_routes.py      # HTTP endpoints for products
│   │   ├── order_routes.py
│   │   └── ...
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── error_handler.py       # Global error handling
│   │   ├── auth.py                # Authentication middleware
│   │   ├── logging.py             # Request logging
│   │   └── cors.py                # CORS configuration
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py
│   │   ├── decorators.py
│   │   ├── helpers.py
│   │   └── ...
│   │
│   ├── services/  (optional)
│   │   ├── __init__.py
│   │   ├── email_service.py
│   │   ├── payment_service.py
│   │   └── ...
│   │
│   ├── __init__.py
│   └── app.py                 # App creation (factory pattern)
│
├── main.py                    # Entry point
├── wsgi.py                    # WSGI entry (for production)
├── requirements.txt
├── .env.example               # Example env variables
├── .gitignore
└── README.md
```

### Node.js/Express Target

```
project-name/
├── src/
│   ├── config/
│   │   ├── index.js           # Configuration
│   │   ├── database.js        # DB connection
│   │   └── constants.js       # Constants
│   │
│   ├── models/
│   │   ├── index.js
│   │   ├── User.js
│   │   ├── Product.js
│   │   └── ...
│   │
│   ├── controllers/
│   │   ├── index.js
│   │   ├── userController.js
│   │   ├── productController.js
│   │   └── ...
│   │
│   ├── routes/
│   │   ├── index.js           # Route aggregator
│   │   ├── userRoutes.js
│   │   ├── productRoutes.js
│   │   └── ...
│   │
│   ├── middleware/
│   │   ├── errorHandler.js
│   │   ├── auth.js
│   │   ├── validation.js
│   │   └── ...
│   │
│   ├── utils/
│   │   ├── validators.js
│   │   ├── helpers.js
│   │   └── ...
│   │
│   ├── services/  (optional)
│   │   ├── emailService.js
│   │   ├── paymentService.js
│   │   └── ...
│   │
│   ├── app.js                 # Express app setup
│   └── server.js              # Server startup (if separate)
│
├── .env.example
├── package.json
├── .gitignore
└── README.md
```

---

## Layer Responsibilities

### 1. Config Layer (`config/`)

**Purpose:** Centralize all configuration and environment setup

**Responsibilities:**
- Load environment variables
- Database connection setup
- Define constants and enums
- Server configuration (port, host)
- API keys and secrets (from env, NOT hardcoded)

**Python Example:**
```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    DATABASE_URL = os.getenv('DATABASE_URL')
    API_KEY = os.getenv('API_KEY')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

config = Config()
```

**Node.js Example:**
```javascript
// config/index.js
require('dotenv').config();

module.exports = {
    port: process.env.PORT || 3000,
    secretKey: process.env.SECRET_KEY,
    database: {
        url: process.env.DATABASE_URL,
    },
    apiKey: process.env.API_KEY,
    corsOrigins: (process.env.CORS_ORIGINS || '*').split(','),
};
```

**Files:**
- `settings.py` (Python) or `index.js` (Node.js)
- `database.py/.js` — DB connection logic
- `constants.py/.js` — Enums, magic numbers as constants

---

### 2. Model Layer (`models/`)

**Purpose:** Define data structures and encapsulate data access logic

**Responsibilities:**
- Entity definitions (fields, types, relationships)
- Data validation methods
- Serialization methods (to_dict, to_json)
- Database operations (via ORM or repository)

**Python Example:**
```python
# models/product.py
from database import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category', backref='products')
    
    def validate(self):
        if len(self.name) < 2: raise ValueError("Name too short")
        if self.price < 0: raise ValueError("Price must be positive")
        if self.stock < 0: raise ValueError("Stock must be positive")
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
        }
    
    @staticmethod
    def from_dict(data):
        product = Product(
            name=data['name'],
            price=data['price'],
            stock=data.get('stock', 0),
            category_id=data.get('category_id')
        )
        product.validate()
        return product
```

**Node.js Example (using Sequelize):**
```javascript
// models/Product.js
const { DataTypes } = require('sequelize');

module.exports = (sequelize) => {
    const Product = sequelize.define('Product', {
        id: {
            type: DataTypes.INTEGER,
            primaryKey: true,
            autoIncrement: true,
        },
        name: {
            type: DataTypes.STRING(200),
            allowNull: false,
        },
        price: {
            type: DataTypes.FLOAT,
            allowNull: false,
        },
        stock: {
            type: DataTypes.INTEGER,
            defaultValue: 0,
        },
    });
    
    Product.associate = (models) => {
        Product.belongsTo(models.Category, { foreignKey: 'categoryId' });
    };
    
    Product.prototype.validate = function() {
        if (this.name.length < 2) throw new Error("Name too short");
        if (this.price < 0) throw new Error("Price must be positive");
    };
    
    Product.prototype.toJSON = function() {
        return {
            id: this.id,
            name: this.name,
            price: this.price,
            stock: this.stock,
        };
    };
    
    return Product;
};
```

**Files:**
- `user.py / User.js`
- `product.py / Product.js`
- `order.py / Order.js`
- etc.

**Key Principle:** Models should NOT directly handle HTTP requests or responses.

---

### 3. Controller Layer (`controllers/`)

**Purpose:** Orchestrate business logic and coordinate between Models and Views

**Responsibilities:**
- Receive input from routes
- Validate input (using validators)
- Call models/services to perform operations
- Handle errors and return appropriate responses
- Transform data if needed

**Python Example:**
```python
# controllers/product_controller.py
from models.product import Product
from utils.validators import validate_product_data

class ProductController:
    @staticmethod
    def list_products():
        """Retrieve all products"""
        try:
            products = Product.query.all()
            return {
                'success': True,
                'data': [p.to_dict() for p in products]
            }, 200
        except Exception as e:
            return {'error': str(e)}, 500
    
    @staticmethod
    def create_product(data):
        """Create new product"""
        try:
            errors = validate_product_data(data)
            if errors:
                return {'errors': errors}, 400
            
            product = Product.from_dict(data)
            db.session.add(product)
            db.session.commit()
            
            return {
                'success': True,
                'data': product.to_dict(),
                'message': 'Product created'
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def update_product(product_id, data):
        """Update existing product"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return {'error': 'Product not found'}, 404
            
            errors = validate_product_data(data)
            if errors:
                return {'errors': errors}, 400
            
            for key, value in data.items():
                setattr(product, key, value)
            
            db.session.commit()
            
            return {
                'success': True,
                'data': product.to_dict()
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
    
    @staticmethod
    def delete_product(product_id):
        """Delete product"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return {'error': 'Product not found'}, 404
            
            db.session.delete(product)
            db.session.commit()
            
            return {'success': True, 'message': 'Product deleted'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500
```

**Node.js Example:**
```javascript
// controllers/productController.js
const { Product } = require('../models');

class ProductController {
    async listProducts(req, res, next) {
        try {
            const products = await Product.findAll();
            res.json({
                success: true,
                data: products.map(p => p.toJSON()),
            });
        } catch (error) {
            next(error);
        }
    }
    
    async createProduct(req, res, next) {
        try {
            const { name, price, stock } = req.body;
            
            // Validation
            if (!name || name.length < 2) {
                return res.status(400).json({
                    error: 'Name must be at least 2 characters'
                });
            }
            if (price < 0) {
                return res.status(400).json({
                    error: 'Price must be positive'
                });
            }
            
            const product = await Product.create({ name, price, stock });
            res.status(201).json({
                success: true,
                data: product.toJSON(),
                message: 'Product created'
            });
        } catch (error) {
            next(error);
        }
    }
    
    // ... other methods
}

module.exports = ProductController;
```

**Key Principle:** Controllers orchestrate, they don't query the database directly (use models) or format HTTP responses directly (use views/routes).

---

### 4. View/Routes Layer (`views/` or `routes/`)

**Purpose:** Define HTTP endpoints and request/response handling

**Responsibilities:**
- Define HTTP routes (GET, POST, PUT, DELETE)
- Extract request parameters
- Call appropriate controller methods
- Format HTTP responses
- Handle HTTP-specific concerns (headers, status codes)

**Python Example:**
```python
# views/product_routes.py
from flask import Blueprint, request, jsonify
from controllers.product_controller import ProductController

product_bp = Blueprint('products', __name__, url_prefix='/products')

@product_bp.route('', methods=['GET'])
def list_products():
    result, status = ProductController.list_products()
    return jsonify(result), status

@product_bp.route('', methods=['POST'])
def create_product():
    data = request.get_json()
    result, status = ProductController.create_product(data)
    return jsonify(result), status

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    result, status = ProductController.get_product(product_id)
    return jsonify(result), status

@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    result, status = ProductController.update_product(product_id, data)
    return jsonify(result), status

@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    result, status = ProductController.delete_product(product_id)
    return jsonify(result), status
```

**Node.js Example:**
```javascript
// routes/productRoutes.js
const express = require('express');
const ProductController = require('../controllers/productController');

const router = express.Router();
const productController = new ProductController();

router.get('/', (req, res, next) => productController.listProducts(req, res, next));
router.post('/', (req, res, next) => productController.createProduct(req, res, next));
router.get('/:productId', (req, res, next) => productController.getProduct(req, res, next));
router.put('/:productId', (req, res, next) => productController.updateProduct(req, res, next));
router.delete('/:productId', (req, res, next) => productController.deleteProduct(req, res, next));

module.exports = router;
```

**Key Principle:** Routes should be thin — just HTTP handling, delegating logic to controllers.

---

### 5. Middleware Layer (`middleware/`)

**Purpose:** Cross-cutting concerns that apply to multiple routes

**Responsibilities:**
- Error handling (centralized)
- Authentication/authorization
- Request logging
- CORS headers
- Request validation
- Response formatting

**Python Example:**
```python
# middleware/error_handler.py
def handle_errors(app):
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
```

**Node.js Example:**
```javascript
// middleware/errorHandler.js
function errorHandler(err, req, res, next) {
    console.error(err);
    
    const status = err.status || 500;
    const message = err.message || 'Internal server error';
    
    res.status(status).json({
        error: message,
        status: status,
    });
}

module.exports = errorHandler;
```

---

### 6. Utils Layer (`utils/`)

**Purpose:** Shared utilities used across layers

**Responsibilities:**
- Validation functions
- Helper functions
- Decorators
- Constants

**Python Example:**
```python
# utils/validators.py
def validate_email(email):
    return '@' in email and '.' in email.split('@')[1]

def validate_required_string(value, min_len=1, max_len=None):
    if not value or len(value) < min_len:
        return False
    if max_len and len(value) > max_len:
        return False
    return True

def validate_product_data(data):
    errors = {}
    if not validate_required_string(data.get('name', ''), min_len=2):
        errors['name'] = 'Name must be at least 2 characters'
    if data.get('price', -1) < 0:
        errors['price'] = 'Price must be positive'
    return errors
```

---

## Request/Response Flow

### Example: GET /products/123

```
1. HTTP Request arrives
   GET /products/123
         ↓
2. Routes layer intercepts
   routes/product_routes.py:@product_bp.route('/<int:product_id>')
         ↓
3. Routes layer calls Controller
   ProductController.get_product(123)
         ↓
4. Controller calls Model
   product = Product.query.get(123)
         ↓
5. Model returns data
   product = <Product object>
         ↓
6. Controller formats response
   result = {'success': True, 'data': product.to_dict()}
         ↓
7. Routes layer sends HTTP response
   return jsonify(result), 200
         ↓
8. HTTP Response sent to client
   {"success": true, "data": {...}}
```

---

## Key MVC Principles

✅ **Models** — No HTTP knowledge. Pure data + business rules.  
✅ **Controllers** — Business logic + orchestration. No HTTP details.  
✅ **Views/Routes** — HTTP-only. Call controllers, format responses.  
✅ **Middleware** — Cross-cutting concerns. Applied to all or multiple routes.  
✅ **Utils** — Reusable functions. No dependencies on specific layers.  
✅ **Config** — All configuration centralized. No hardcoded values.  

---

## Testing Benefits

With proper MVC separation:

```python
# Unit test a Model (no DB, no HTTP)
def test_product_validation():
    product = Product(name='Test', price=-5)
    with pytest.raises(ValueError):
        product.validate()

# Unit test a Controller (mock Model)
def test_create_product():
    mock_db = Mock()
    data = {'name': 'Test', 'price': 10}
    result = ProductController.create_product(data)
    assert result[1] == 201

# Integration test a Route (with real HTTP)
def test_api_create_product(client):
    response = client.post('/products', json={'name': 'Test', 'price': 10})
    assert response.status_code == 201
```

---

## Summary

| Layer | Responsibility | Examples |
|:---|:---|:---|
| **Config** | Centralize all configuration | env vars, DB setup, constants |
| **Model** | Data + business rules | entities, validation, serialization |
| **Controller** | Orchestrate logic | process input, call models, handle errors |
| **View/Routes** | HTTP handling | define endpoints, call controllers |
| **Middleware** | Cross-cutting concerns | error handling, auth, logging |
| **Utils** | Shared utilities | validators, helpers, decorators |

Refactored projects should follow this pattern for all 3 projects (Python/Flask, Node.js/Express, and any other stack).
