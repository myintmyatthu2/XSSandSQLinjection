from flask import Flask, render_template, request, redirect, url_for, session, make_response
import sqlite3, os, datetime

app = Flask(__name__)
app.secret_key = "aod_full_project_secret"
DB = "aod_lab.db"

# Security configuration flags
app.config['PROTECTION_XSS'] = False
app.config['PROTECTION_SQLI'] = False
app.config['PROTECTION_CSRF'] = False
app.config['SECURE_COOKIES'] = False

def get_db():
    return sqlite3.connect(DB)

def init_db():
    first = not os.path.exists(DB)
    conn = get_db()
    c = conn.cursor()
    # users
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )""")
    # products
    c.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price INTEGER
    )""")
    # orders
    c.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        product_id INTEGER,
        price_paid INTEGER,
        ts TEXT
    )""")
    # feedback (name + message)
    c.execute("""CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY,
        name TEXT,
        message TEXT,
        ts TEXT
    )""")
    # leaks (simulated attacker inbox)
    c.execute("""CREATE TABLE IF NOT EXISTS leaks (
        id INTEGER PRIMARY KEY,
        data TEXT,
        ts TEXT
    )""")

    if first:
        # seed users
        c.execute("INSERT OR IGNORE INTO users (username,password,role) VALUES ('admin','admin123','admin')")
        c.execute("INSERT OR IGNORE INTO users (username,password,role) VALUES ('alice','alice123','user')")
        c.execute("INSERT OR IGNORE INTO users (username,password,role) VALUES ('bob','bob123','user')")
        # seed products
        c.execute("INSERT INTO products (name, price) VALUES ('Laptop', 1000)")
        c.execute("INSERT INTO products (name, price) VALUES ('Phone', 500)")
        c.execute("INSERT INTO products (name, price) VALUES ('Headphones', 100)")

    conn.commit()
    conn.close()

init_db()

# helpers
def role_required(role_name):
    def deco(f):
        def wrapper(*args, **kwargs):
            if 'username' not in session or session.get('role') != role_name:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return deco

@app.route('/')
def index():
    return redirect(url_for('feedback'))

# LOGIN / LOGOUT
@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
        u = request.form.get('username','').strip()
        p = request.form.get('password','').strip()
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT id, role FROM users WHERE username=? AND password=?", (u,p))
        row = c.fetchone(); conn.close()
        if row:
            session['user_id'] = row[0]
            session['username'] = u
            session['role'] = row[1]
            resp = make_response(redirect(url_for('index')))
            resp.set_cookie('aod_session', f"user={u};role={row[1]}")
            return resp
        else:
            error = "Invalid credentials"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('aod_session')
    return resp

# FEEDBACK (name + message) with special markers
@app.route('/feedback', methods=['GET','POST'])
def feedback():
    leaked = None
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        message = request.form.get('message','').strip()
        ts = datetime.datetime.utcnow().isoformat()
        
        # SPECIAL MARKERS HANDLING - THIS IS CRITICAL
        if message == '<LEAK_ADMIN>':
            leaked = 'admin:admin123'
            conn = get_db(); c = conn.cursor(); c.execute("INSERT INTO leaks (data, ts) VALUES (?,?)", (leaked, ts)); conn.commit(); conn.close()
        elif message == '<LEAK_USERS>':
            leaked = 'alice:alice123, bob:bob123'
            conn = get_db(); c = conn.cursor(); c.execute("INSERT INTO leaks (data, ts) VALUES (?,?)", (leaked, ts)); conn.commit(); conn.close()
        elif message == '<LEAK_ALL>':
            leaked = 'admin:admin123; alice:alice123; bob:bob123'
            conn = get_db(); c = conn.cursor(); c.execute("INSERT INTO leaks (data, ts) VALUES (?,?)", (leaked, ts)); conn.commit(); conn.close()
        elif message == '<XSS_DEMO>':
            # This will demonstrate XSS when viewed in admin review
            message = '<script>alert("XSS Demo! Cookies: " + document.cookie)</script>'
            conn = get_db()
            c = conn.cursor()
            c.execute("INSERT INTO feedback (name, message, ts) VALUES (?,?,?)", 
                     (name, message, ts))
            conn.commit()
            conn.close()
            return redirect(url_for('feedback'))
        else:
            # Normal feedback submission
            conn = get_db(); c = conn.cursor()
            c.execute("INSERT INTO feedback (name, message, ts) VALUES (?,?,?)", (name, message, ts))
            conn.commit(); conn.close()
            return redirect(url_for('feedback'))
    
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT name, message, ts FROM feedback ORDER BY id DESC LIMIT 20")
    rows = c.fetchall(); conn.close()
    
    return render_template('feedback.html', rows=rows, leaked=leaked)

# ADMIN review - intentionally vulnerable to stored XSS and SQL injection
@app.route('/admin/review')
@role_required('admin')
def admin_review():
    conn = get_db()
    c = conn.cursor()
    
    # Get search parameter from URL
    search = request.args.get('search', '')
    error = None
    
    try:
        # Vulnerable query for SQL injection demo
        if search:
            if app.config['PROTECTION_SQLI']:
                # Secure version with parameterized queries
                c.execute("SELECT id, name, message, ts FROM feedback WHERE message LIKE ? ORDER BY id DESC LIMIT 50", 
                         (f"%{search}%",))
            else:
                # This is vulnerable to SQL injection - string concatenation
                query = f"SELECT id, name, message, ts FROM feedback WHERE message LIKE '%{search}%' ORDER BY id DESC LIMIT 50"
                print(f"Executing vulnerable query: {query}")  # For debugging
                c.execute(query)
        else:
            # No search term - show all
            c.execute("SELECT id, name, message, ts FROM feedback ORDER BY id DESC LIMIT 50")
        
        rows = c.fetchall()
        
    except sqlite3.Error as e:
        rows = []
        error = f"SQL Error: {str(e)}"
        print(f"SQL Error: {e}")
        
    finally:
        conn.close()
    
    # Pass config values to template
    return render_template('admin_review.html', 
                         rows=rows, 
                         search=search,
                         error=error,
                         protection_sqli=app.config['PROTECTION_SQLI'],
                         protection_xss=app.config['PROTECTION_XSS'])

# Attacker inbox to view captured leaks (lab-only)
@app.route('/attacker')
def attacker():
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT id, data, ts FROM leaks ORDER BY id DESC LIMIT 100")
    rows = c.fetchall(); conn.close()
    return render_template('attacker.html', rows=rows)

# ADMIN dashboard - manage products
@app.route('/admin/dashboard', methods=['GET','POST'])
@role_required('admin')
def admin_dashboard():
    conn = get_db(); c = conn.cursor()
    if request.method == 'POST':
        pid = request.form.get('product_id')
        price = request.form.get('price')
        c.execute("UPDATE products SET price=? WHERE id=?", (price, pid))
        conn.commit()
    c.execute("SELECT id, name, price FROM products ORDER BY id")
    products = c.fetchall(); conn.close()
    return render_template('admin_dashboard.html', products=products)

# SHOP - user view
@app.route('/shop')
def shop():
    if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT id, name, price FROM products ORDER BY id")
    products = c.fetchall(); conn.close()
    return render_template('shop.html', products=products)

# BUY - vulnerable (trusts client price)
@app.route('/buy', methods=['POST'])
def buy():
    if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    product_id = request.form.get('product_id')
    price_paid = request.form.get('price')
    ts = datetime.datetime.utcnow().isoformat()
    conn = get_db(); c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, product_id, price_paid, ts) VALUES (?,?,?,?)", (session['user_id'], product_id, price_paid, ts))
    conn.commit(); conn.close()
    return render_template('success.html', price=price_paid)

# Dashboards redirects
@app.route('/admin/home')
@role_required('admin')
def admin_home():
    return redirect(url_for('admin_dashboard'))

@app.route('/user/home')
def user_home():
    if 'username' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    return redirect(url_for('shop'))
    
# ADMIN orders view - see all purchases and detect price tampering
@app.route('/admin/orders')
@role_required('admin')
def admin_orders():
    conn = get_db()
    c = conn.cursor()
    
    # Get all orders with user and product information
    c.execute("""
        SELECT orders.id, users.username, products.name, products.price, 
               orders.price_paid, orders.ts 
        FROM orders 
        JOIN users ON orders.user_id = users.id 
        JOIN products ON orders.product_id = products.id 
        ORDER BY orders.id DESC
    """)
    orders = c.fetchall()
    conn.close()
    
    # Calculate statistics
    total_orders = len(orders)
    tampered_orders = 0
    total_loss = 0
    
    for order in orders:
        actual_price = order[3]  # products.price
        price_paid = order[4]    # orders.price_paid
        if price_paid != actual_price:
            tampered_orders += 1
            total_loss += (actual_price - price_paid)
    
    return render_template('admin_orders.html', 
                         orders=orders,
                         total_orders=total_orders,
                         tampered_orders=tampered_orders,
                         total_loss=total_loss)
    
    
    

if __name__ == '__main__':
    app.run(debug=True)
