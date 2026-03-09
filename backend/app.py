from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key, Attr
import json
import uuid
import os

# ============================================================
# APP SETUP
# ============================================================
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'homemade_pickles_secret_2024')

# ============================================================
# AWS CONFIGURATION
# Use AWS credentials from environment or AWS CLI profile
# ============================================================
AWS_REGION = os.environ.get('AWS_REGION', 'ap-south-1')

# Connect to DynamoDB
try:
    # Try to use default AWS credentials (from ~/.aws/credentials or EC2 instance role)
    dynamodb = boto3.resource(
    'dynamodb',
    region_name='ap-south-1'
)
except Exception as e:
    print(f"Warning: Could not connect to AWS DynamoDB: {e}")
    dynamodb = None

# Your 3 DynamoDB tables
users_table = dynamodb.Table('Users') if dynamodb else None
orders_table = dynamodb.Table('Orders') if dynamodb else None
products_table = dynamodb.Table('Products') if dynamodb else None

# ============================================================
# PRODUCT CATALOG - LIMITED TO 10 PRODUCTS
# ============================================================
PRODUCTS = [
    # ── NON-VEG PICKLES (3 products) ──────────────────────────────
    {
        "ProductID": "NV001", "category": "non_veg_pickles",
        "name": "Chicken Pickle",
        "desc": "Tender chicken slow-cooked with red chilli, sesame and mustard oil.",
        "img": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600",
        "tag": "Bestseller",
        "weights": {"250": 280, "500": 520},
        "rating": 4.8,
        "price": 280
    },
    {
        "ProductID": "NV002", "category": "non_veg_pickles",
        "name": "Mutton Pickle",
        "desc": "Succulent mutton pieces marinated in Andhra-style spice blend.",
        "img": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600",
        "tag": "Spicy",
        "weights": {"250": 320, "500": 600},
        "rating": 4.7,
        "price": 320
    },
    {
        "ProductID": "NV003", "category": "non_veg_pickles",
        "name": "Fish Pickle",
        "desc": "Coastal-style fish pickle with raw mango and kokum.",
        "img": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600",
        "tag": "Coastal",
        "weights": {"250": 260, "500": 490},
        "rating": 4.6,
        "price": 260
    },

    # ── VEG PICKLES (4 products) ──────────────────────────────────
    {
        "ProductID": "VP001", "category": "veg_pickles",
        "name": "Mango Pickle",
        "desc": "Raw mango chunks tempered with mustard, fenugreek and chilli powder.",
        "img": "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600",
        "tag": "Classic",
        "weights": {"250": 120, "500": 220},
        "rating": 4.8,
        "price": 120
    },
    {
        "ProductID": "VP002", "category": "veg_pickles",
        "name": "Lemon Pickle",
        "desc": "Sun-soaked lemons with spices — bright, tangy and digestive.",
        "img": "https://images.unsplash.com/photo-1587486936739-78a3a6d4a176?w=600",
        "tag": "Tangy",
        "weights": {"250": 110, "500": 200},
        "rating": 4.6,
        "price": 110
    },
    {
        "ProductID": "VP003", "category": "veg_pickles",
        "name": "Tomato Pickle",
        "desc": "Slow-cooked tomato relish with garlic and tamarind.",
        "img": "https://images.unsplash.com/photo-1558818498-28c1e002b655?w=600",
        "tag": "Fresh",
        "weights": {"250": 130, "500": 240},
        "rating": 4.5,
        "price": 130
    },
    {
        "ProductID": "VP004", "category": "veg_pickles",
        "name": "Green Chilli Pickle",
        "desc": "Whole green chillies preserved in spiced mustard oil.",
        "img": "https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=600",
        "tag": "Hot",
        "weights": {"250": 100, "500": 185},
        "rating": 4.4,
        "price": 100
    },

    # ── SNACKS (3 products) ───────────────────────────────────────
    {
        "ProductID": "SN001", "category": "snacks",
        "name": "Ragi Laddu",
        "desc": "Finger-millet laddus sweetened with jaggery.",
        "img": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
        "tag": "Healthy",
        "weights": {"250": 350, "500": 700},
        "rating": 4.6,
        "price": 350
    },
    {
        "ProductID": "SN002", "category": "snacks",
        "name": "Dry Fruit Laddu",
        "desc": "Rich laddus loaded with cashews, almonds, and dates.",
        "img": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
        "tag": "Premium",
        "weights": {"250": 500, "500": 1000},
        "rating": 4.9,
        "price": 500
    },
    {
        "ProductID": "SN003", "category": "snacks",
        "name": "Kara Boondi",
        "desc": "Crispy spiced boondi — perfect tea-time companion.",
        "img": "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600",
        "tag": "Spicy",
        "weights": {"250": 250, "500": 500},
        "rating": 4.5,
        "price": 250
    },
]

# ============================================================
# HELPERS
# ============================================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def get_product_by_id(pid):
    return next((p for p in PRODUCTS if p['ProductID'] == str(pid)), None)

def safe_json(data):
    return json.loads(json.dumps(data, default=decimal_default))

# ============================================================
# PAGE ROUTES
# ============================================================
@app.route('/')
def index():
    return render_template('index.html', products=PRODUCTS)

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/non_veg_pickles')
def non_veg_pickles():
    products = [p for p in PRODUCTS if p['category'] == 'non_veg_pickles']
    return render_template('non_veg_pickles.html', products=products)

@app.route('/veg_pickles')
def veg_pickles():
    products = [p for p in PRODUCTS if p['category'] == 'veg_pickles']
    return render_template('veg_pickles.html', products=products)

@app.route('/snacks')
def snacks():
    products = [p for p in PRODUCTS if p['category'] == 'snacks']
    return render_template('snacks.html', products=products)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/orders')
@login_required
def orders():
    """Display user's order history"""
    return render_template('orders.html')

# ============================================================
# API AUTH ENDPOINTS (for frontend)
# ============================================================
@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    """Check if user is logged in"""
    if session.get('logged_in'):
        return jsonify({
            'authenticated': True,
            'user': {
                'UserID': session.get('UserID'),
                'username': session.get('username'),
                'email': session.get('email')
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email and password are required'}), 400

    user_id = str(uuid.uuid4())
    try:
        if users_table:
            # Check if user exists
            existing = users_table.scan(
                FilterExpression=Attr('email').eq(email)
            )
            if existing.get('Items'):
                return jsonify({'error': 'Email already exists'}), 400

            # Create new user
            users_table.put_item(Item={
                'UserID': user_id,
                'username': name,
                'email': email,
                'phone': phone,
                'password': generate_password_hash(password),
                'created_at': datetime.now().isoformat()
            })
        
        # Auto-login after signup
        session['logged_in'] = True
        session['UserID'] = user_id
        session['username'] = name
        session['email'] = email
        session['cart'] = []
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': {
                'UserID': user_id,
                'username': name,
                'email': email
            }
        })
    except Exception as e:
        app.logger.error(f"Registration error: {e}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    data = request.get_json()
    
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        if users_table:
            result = users_table.scan(FilterExpression=Attr('email').eq(email))
            items = result.get('Items', [])
            
            if items and check_password_hash(items[0]['password'], password):
                user = items[0]
                session['logged_in'] = True
                session['UserID'] = user['UserID']
                session['username'] = user['username']
                session['email'] = user.get('email', '')
                session['cart'] = []
                
                return jsonify({
                    'success': True,
                    'message': 'Login successful',
                    'user': {
                        'UserID': user['UserID'],
                        'username': user['username'],
                        'email': user.get('email', '')
                    }
                })
        
        return jsonify({'error': 'Invalid email or password'}), 401
    except Exception as e:
        app.logger.error(f"Login error: {e}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """API endpoint for user logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# ============================================================
# AUTH ROUTES (HTML pages)
# ============================================================
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            return render_template('signup.html', error='All fields are required.')

        user_id = str(uuid.uuid4())
        try:
            if users_table:
                # Check if user exists
                existing = users_table.scan(
                    FilterExpression=Attr('username').eq(username) | Attr('email').eq(email)
                )
                if existing.get('Items'):
                    return render_template('signup.html', error='Username or email already exists.')

                # Create new user
                users_table.put_item(Item={
                    'UserID': user_id,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'password': generate_password_hash(password),
                    'created_at': datetime.now().isoformat()
                })
            
            # Auto-login after signup
            session['logged_in'] = True
            session['UserID'] = user_id
            session['username'] = username
            session['email'] = email
            session['cart'] = []
            return redirect(url_for('home'))
        except Exception as e:
            app.logger.error(f"Signup error: {e}")
            return render_template('signup.html', error=f'Signup failed: {str(e)}')

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error='Username and password are required.')

        try:
            if users_table:
                result = users_table.scan(FilterExpression=Attr('username').eq(username))
                items = result.get('Items', [])
                
                if items and check_password_hash(items[0]['password'], password):
                    user = items[0]
                    session['logged_in'] = True
                    session['UserID'] = user['UserID']
                    session['username'] = user['username']
                    session['email'] = user.get('email', '')
                    session['cart'] = []
                    return redirect(url_for('home'))
            
            return render_template('login.html', error='Invalid username or password.')
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            return render_template('login.html', error=f'Login failed: {str(e)}')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ============================================================
# CHECKOUT & ORDER ROUTES
# ============================================================
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        payment = request.form.get('payment', 'cod')
        cart_data = request.form.get('cart_data', '[]')
        total_amount = request.form.get('total_amount', '0')

        if not name or not phone or not address:
            return render_template('checkout.html', error='All delivery details are required.')

        try:
            cart_items = json.loads(cart_data)
            if not cart_items:
                return render_template('checkout.html', error='Cart is empty.')

            # Create order in DynamoDB
            order_id = str(uuid.uuid4())
            
            if orders_table:
                orders_table.put_item(Item={
                    'OrderID': order_id,
                    'UserID': session.get('UserID', ''),
                    'username': session.get('username', ''),
                    'items': cart_items,
                    'total_amount': str(total_amount),
                    'payment_method': payment,
                    'shipping_address': {
                        'name': name,
                        'phone': phone,
                        'address': address
                    },
                    'status': 'placed',
                    'timestamp': datetime.now().isoformat()
                })
            
            # Clear session cart
            session['cart'] = []
            return redirect(url_for('success'))
        except Exception as e:
            app.logger.error(f"Checkout error: {e}")
            return render_template('checkout.html', error=f'Order failed: {str(e)}')

    return render_template('checkout.html')

@app.route('/success')
@login_required
def success():
    return render_template('sucess.html')

# ============================================================
# API ROUTES
# ============================================================
@app.route('/api/products', methods=['GET'])
def api_products():
    """Get products with optional filtering"""
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').lower()
    
    result = PRODUCTS.copy()
    
    if category != 'all':
        cat_map = {
            'non-veg': ['non_veg_pickles'],
            'veg': ['veg_pickles'],
            'snacks': ['snacks']
        }
        allowed = cat_map.get(category, [category])
        result = [p for p in result if p['category'] in allowed]
    
    if search:
        result = [p for p in result if search in p['name'].lower()]
    
    return jsonify({'products': result, 'total': len(result)})

@app.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    """Get all orders for the logged-in user"""
    try:
        if not orders_table:
            return jsonify({'error': 'Database not available'}), 500
        
        user_id = session.get('UserID', '')
        
        # Scan orders table and filter by UserID
        response = orders_table.scan(
            FilterExpression=Attr('UserID').eq(user_id)
        )
        
        orders = response.get('Items', [])
        
        # Sort by timestamp descending (newest first)
        orders.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return jsonify({'orders': safe_json(orders)})
    except Exception as e:
        app.logger.error(f"Get orders error: {e}")
        return jsonify({'error': f'Failed to fetch orders: {str(e)}'}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
@login_required
def api_get_order(order_id):
    """Get a specific order by ID"""
    try:
        if not orders_table:
            return jsonify({'error': 'Database not available'}), 500
        
        response = orders_table.get_item(Key={'OrderID': order_id})
        order = response.get('Item')
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Verify order belongs to logged-in user
        if order.get('UserID') != session.get('UserID'):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({'order': safe_json(order)})
    except Exception as e:
        app.logger.error(f"Get order error: {e}")
        return jsonify({'error': f'Failed to fetch order: {str(e)}'}), 500

# ============================================================
# HEALTH CHECK
# ============================================================
@app.route('/health')
def health():
    try:
        if users_table:
            users_table.load()
            db = 'connected'
        else:
            db = 'not configured'
    except Exception as e:
        db = f'error: {e}'
    return jsonify({
        'status': 'ok',
        'dynamodb': db,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/recommendations')
def recommendations():
    return jsonify({"recommendations": PRODUCTS[:4]})

@app.route('/api/orders', methods=['POST'])
@login_required
def api_create_order():
    try:
        data = request.get_json()

        items = data.get('items', [])
        payment_method = data.get('payment_method', 'cod')
        shipping_address = data.get('shipping_address', {})

        if not items:
            return jsonify({"error": "Cart is empty"}), 400

        order_id = str(uuid.uuid4())

        # calculate total
        total = 0
        order_items = []

        for i in items:
            product = get_product_by_id(i.get("product_id"))
            qty = int(i.get("quantity", 1))

            if not product:
                continue

            price = product.get("price", 0)
            total += price * qty

            order_items.append({
                "product_id": product["ProductID"],
                "name": product["name"],
                "price": price,
                "qty": qty
            })

        order_data = {
            "OrderID": order_id,
            "UserID": session.get("UserID"),
            "items": order_items,
            "total_amount": total,
            "payment_method": payment_method,
            "shipping_address": shipping_address,
            "status": "placed",
            "timestamp": datetime.now().isoformat()
        }

        if orders_table:
            orders_table.put_item(Item=order_data)

        return jsonify({
            "success": True,
            "order": {
                "order_id": order_id,
                "total": total
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)