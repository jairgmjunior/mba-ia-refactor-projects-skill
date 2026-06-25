================================
ARCHITECTURE AUDIT REPORT
================================

**Project:** ecommerce-api-legacy  
**Stack:** Node.js 14+ + Express + SQLite3  
**Database:** SQLite (in-memory)  
**Domain:** LMS API with checkout flow  
**Files Analyzed:** 3 source files (app.js, AppManager.js, utils.js)  
**Approx. Lines of Code:** ~250

---

## Executive Summary

| Severity | Count |
|:---:|:---:|
| CRITICAL | 3 |
| HIGH | 2 |
| MEDIUM | 2 |
| LOW | 1 |
| **TOTAL** | **8** |

**Overall Assessment:** Critical security vulnerabilities with exposed production credentials, insecure cryptography, and god class pattern. Payment processing logic mixed with DB and routing. High risk for security breach and production failures.

---

## Detailed Findings

### [CRITICAL] Hardcoded Credentials in Code

**File:** utils.js:2-6  
**Description:** Production credentials hardcoded directly in source code:
- Database password: "senha_super_secreta_prod_123"
- Payment gateway API key: "pk_live_1234567890abcdef"
- SMTP user: "no-reply@fullcycle.com.br"
- Server port: 3000

**Impact:** If repository is compromised or code is shared, attacker gains:
- Database access (can read/modify all user and payment data)
- Payment processing capability (can charge cards fraudulently)
- Email sending capability (can spam or phish users)

This is a CRITICAL security incident waiting to happen.

**Current Code:**
```javascript
const config = {
    dbUser: "admin_master",
    dbPass: "senha_super_secreta_prod_123",
    paymentGatewayKey: "pk_live_1234567890abcdef",
    smtpUser: "no-reply@fullcycle.com.br",
    port: 3000
};
```

**Refactored Code:**
```javascript
// config/index.js
require('dotenv').config();

module.exports = {
    dbUser: process.env.DB_USER,
    dbPass: process.env.DB_PASSWORD,
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    smtpUser: process.env.SMTP_USER,
    port: process.env.PORT || 3000
};

// .env (git-ignored)
DB_USER=admin_master
DB_PASSWORD=senha_super_secreta_prod_123
PAYMENT_GATEWAY_KEY=pk_live_1234567890abcdef
SMTP_USER=no-reply@fullcycle.com.br
PORT=3000

// .env.example (committed)
DB_USER=
DB_PASSWORD=
PAYMENT_GATEWAY_KEY=
SMTP_USER=
PORT=3000
```

---

### [CRITICAL] Insecure Cryptography / Fake Crypto

**File:** utils.js:16-22  
**Description:** Password "encryption" uses fake cryptography that is NOT actually encryption:

```javascript
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

This function:
1. Just repeats base64 encoding 10,000 times
2. Takes first 10 characters of result
3. Is completely reversible
4. Provides NO security against password attacks
5. All users with same password get SAME hash

**Impact:** 
- Passwords are NOT actually protected
- If database is compromised, all passwords are exposed in plaintext
- Cannot defend against rainbow table attacks
- Violates PCI-DSS compliance

**Current Code (INSECURE):**
```javascript
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}

// Usage
const hash = badCrypto("user_password");  // Always same hash for same password!
```

**Refactored Code (SECURE):**
```javascript
// Install: npm install bcrypt
const bcrypt = require('bcrypt');

async function hashPassword(password) {
    const saltRounds = 10;
    return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
}

// Usage
const hashedPassword = await hashPassword("user_password");  // Different each time!
const isValid = await verifyPassword("user_password", hashedPassword);
```

---

### [CRITICAL] God Class Pattern

**File:** AppManager.js:1-150  
**Description:** Single class handles all responsibilities:
- Database initialization (lines 5-20)
- Route setup (lines 22-100)
- Business logic for checkout (lines 25-70)
- Payment processing (lines 40-55)
- User creation (lines 60-75)
- Enrollment logic (lines 50-65)
- Audit logging (lines 68-72)
- Financial report generation (lines 100-150)

All mixed in ONE class, making it impossible to test or maintain.

**Impact:** 
- Cannot unit test payment logic without DB
- Cannot test routes separately
- Cannot reuse business logic elsewhere
- Any change might break 5 different features
- Violates Single Responsibility Principle

**Current Structure (Bad):**
```
AppManager.js (150 lines)
├── DB setup
├── All routes
├── Payment processing
├── User management
├── Enrollment logic
└── Reporting
```

**Refactored Structure (Good):**
```
src/
├── config/
│   ├── database.js
│   └── settings.js
├── models/
│   ├── User.js
│   ├── Course.js
│   ├── Enrollment.js
│   └── Payment.js
├── controllers/
│   ├── authController.js
│   ├── checkoutController.js
│   ├── courseController.js
│   └── reportController.js
├── routes/
│   ├── authRoutes.js
│   ├── checkoutRoutes.js
│   ├── courseRoutes.js
│   └── reportRoutes.js
├── middleware/
│   ├── errorHandler.js
│   └── auth.js
├── services/
│   ├── paymentService.js
│   └── auditService.js
└── app.js
```

---

### [HIGH] Callback Hell / Deeply Nested Callbacks

**File:** AppManager.js:25-80  
**Description:** Multiple levels of nested callbacks making error handling difficult and code hard to follow:

```javascript
app.post('/api/checkout', (req, res) => {
    this.db.get("SELECT * FROM courses", (err, course) => {
        this.db.get("SELECT * FROM users", (err, user) => {
            if (!user) {
                this.db.run("INSERT INTO users", (err) => {
                    this.db.run("INSERT INTO enrollments", (err) => {
                        this.db.run("INSERT INTO payments", (err) => {
                            this.db.run("INSERT INTO audit_logs", (err) => {
                                res.json({success: true});
                            });
                        });
                    });
                });
            }
        });
    });
});
```

**Impact:** 
- Hard to follow execution flow
- Error handling scattered and repeated
- Difficult to debug (stack traces confusing)
- Easy to miss error cases

**Refactored Code (async/await):**
```javascript
app.post('/api/checkout', async (req, res, next) => {
    try {
        const course = await db.get('SELECT * FROM courses WHERE id = ?', [courseId]);
        if (!course) return res.status(404).json({error: 'Course not found'});
        
        let user = await db.get('SELECT * FROM users WHERE email = ?', [email]);
        if (!user) {
            user = await db.run('INSERT INTO users VALUES (?, ?, ?)', [name, email, hash]);
        }
        
        const enrollment = await db.run('INSERT INTO enrollments VALUES (?, ?)', [user.id, course.id]);
        const payment = await db.run('INSERT INTO payments VALUES (?, ?, ?)', [enrollment.id, course.price, 'PAID']);
        await auditService.log(`Checkout course ${course.id} by user ${user.id}`);
        
        res.json({success: true, enrollmentId: enrollment.id});
    } catch (error) {
        next(error);
    }
});
```

---

### [HIGH] Global Mutable State

**File:** utils.js:8-9  
**Description:** Global variables that can be mutated from anywhere without synchronization:

```javascript
let globalCache = {};
let totalRevenue = 0;

function logAndCache(key, data) {
    globalCache[key] = data;  // ← Mutation without locks
}
```

Other parts of code can modify globalCache and totalRevenue unpredictably.

**Impact:** 
- Race conditions in concurrent requests
- Unpredictable behavior
- Cannot reset state between tests
- Memory leaks (cache never cleared)

**Refactored Code (Encapsulated Service):**
```javascript
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
    
    reset() {
        this.total = 0;
    }
}

// Usage with dependency injection
const cacheService = new CacheService();
const revenueService = new RevenueService();

app.post('/checkout', async (req, res) => {
    // ...
    cacheService.set(`checkout_${userId}`, enrollmentData);
    revenueService.add(course.price);
    // ...
});
```

---

### [MEDIUM] N+1 Query Problem

**File:** AppManager.js:100-120  
**Description:** Financial report loops over all courses and executes a separate query for each:

```javascript
let coursesPending = courses.length;
courses.forEach(c => {
    // This query runs once PER COURSE
    this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
        // ...
        coursesPending--;
    });
});
```

With 1000 courses, this executes 1001 queries (1 initial + 1000 inside loop).

**Impact:** 
- Severe performance degradation
- Database connection exhaustion
- Timeouts on reports
- Poor scalability

**Refactored Code (JOIN):**
```javascript
async function getFinancialReport() {
    const report = await db.all(`
        SELECT 
            c.title,
            COUNT(e.id) as total_enrollments,
            SUM(p.amount) as total_revenue,
            COUNT(CASE WHEN p.status = 'PAID' THEN 1 END) as paid_enrollments
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        LEFT JOIN payments p ON e.id = p.enrollment_id
        GROUP BY c.id
    `);
    return report;  // Single query!
}
```

---

### [MEDIUM] Inadequate Card Validation

**File:** AppManager.js:27  
**Description:** Card validation only checks if card starts with "4":

```javascript
let status = cc.startsWith("4") ? "PAID" : "DENIED";
```

**Impact:** 
- Any card starting with "4" is accepted (regardless of validity)
- No checksum verification (Luhn algorithm)
- No expiry check
- No CVV validation
- Fraudulent transactions can be approved

**Recommendation:** Use proper payment gateway library (Stripe, Square, etc.).

---

### [LOW] Unclear Variable Names

**File:** AppManager.js:25-28  
**Description:** Request body parameters use cryptic abbreviations:

```javascript
let u = req.body.usr;      // → username
let e = req.body.eml;      // → email
let p = req.body.pwd;      // → password
let cid = req.body.c_id;   // → courseId
let cc = req.body.card;    // → cardNumber
```

**Impact:** Reduces code readability and increases bugs.

**Refactored Code:**
```javascript
const { username, email, password, courseId, cardNumber } = req.body;
```

---

## Refactoring Recommendations

### Priority 1: CRITICAL (Must Fix Immediately)
1. Extract secrets to env vars
2. Replace fake crypto with bcrypt
3. Separate God Class into modules

### Priority 2: HIGH (Should Fix)
1. Convert callbacks to async/await
2. Encapsulate global state in services

### Priority 3: MEDIUM (Should Fix)
1. Fix N+1 query with JOINs
2. Add proper card validation

### Priority 4: LOW (Nice-to-Have)
1. Rename variables for clarity

---

## Validation Checklist (Post-Refactor)

- [ ] Application starts without errors
- [ ] All endpoints respond correctly
- [ ] Database initializes properly
- [ ] No hardcoded secrets in code
- [ ] Passwords hashed with bcrypt
- [ ] Async/await instead of callbacks
- [ ] Services properly injected
- [ ] Financial report uses JOINs (fast)
- [ ] Error handling centralized
- [ ] Variable names clarified

---

## Estimated Effort

| Task | Effort | Priority |
|:---|:---:|:---:|
| Extract secrets | 1 hour | MUST |
| Implement bcrypt | 1.5 hours | MUST |
| Refactor to async/await | 2 hours | MUST |
| Separate modules (MVC) | 3 hours | MUST |
| Encapsulate services | 1.5 hours | SHOULD |
| Fix N+1 queries | 1 hour | SHOULD |
| Add card validation | 1 hour | COULD |
| **Total** | **11 hours** | - |

---

**Generated:** 2026-06-06  
**Project:** ecommerce-api-legacy  
**Analyst:** Architectural Audit Skill  
**Severity Distribution:** 3 CRITICAL (37.5%) | 2 HIGH (25%) | 2 MEDIUM (25%) | 1 LOW (12.5%)
