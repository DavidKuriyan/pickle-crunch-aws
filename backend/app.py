from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from decimal import Decimal
import boto3
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
# On your EC2, set these before running:
#   export AWS_ACCESS_KEY_ID=AKIA...
#   export AWS_SECRET_ACCESS_KEY=your_secret...
#   export AWS_REGION=ap-south-1
#   python app.py
# ============================================================
AWS_ACCESS_KEY_ID     = os.environ.get('AWS_ACCESS_KEY_ID', 'AKIAUTKU2AVYXWVVWEMM')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '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')
AWS_REGION            = os.environ.get('AWS_REGION', 'ap-south-1')

# Connect to DynamoDB using AWS CLI credentials
dynamodb = boto3.resource(
    'dynamodb',
    region_name='ap-south-1'
)

# Your 3 DynamoDB tables (partition keys as in your console)
users_table    = dynamodb.Table('Users')     # PK: UserID  (String)
orders_table   = dynamodb.Table('Orders')    # PK: OrderID (String)
products_table = dynamodb.Table('Products')  # PK: ProductID (String)

# ============================================================
# PRODUCT CATALOG
# ============================================================
PRODUCTS = [
    # ── NON-VEG PICKLES ──────────────────────────────────────────────────────
    {'ProductID': '1',  'name': 'Chicken Pickle',           'category': 'non_veg_pickles', 'tag': 'Best Seller', 'price': 600,  'weight': '250g', 'rating': 4.8, 'desc': 'Tender chicken slow-cooked in bold Andhra spices and tangy brine.',        'img': 'https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600', 'weights': {'250': 600,  '500': 1200, '1000': 1800}},
    {'ProductID': '2',  'name': 'Fish Pickle',              'category': 'non_veg_pickles', 'tag': 'Spicy',       'price': 200,  'weight': '250g', 'rating': 4.5, 'desc': 'Coastal-style fish pickle with mustard and fenugreek.',                    'img': 'https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600', 'weights': {'250': 200,  '500': 400,  '1000': 800}},
    {'ProductID': '3',  'name': 'Gongura Mutton',           'category': 'non_veg_pickles', 'tag': 'Signature',   'price': 400,  'weight': '250g', 'rating': 4.9, 'desc': 'Premium mutton with tangy gongura leaves — a true Andhra classic.',       'img': 'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600', 'weights': {'250': 400,  '500': 800,  '1000': 1600}},
    {'ProductID': '4',  'name': 'Mutton Pickle',            'category': 'non_veg_pickles', 'tag': 'Premium',     'price': 400,  'weight': '250g', 'rating': 4.7, 'desc': 'Slow-marinated mutton in aromatic masala blend.',                         'img': 'https://images.unsplash.com/photo-1545247181-516773cae754?w=600', 'weights': {'250': 400,  '500': 800,  '1000': 1600}},
    {'ProductID': '5',  'name': 'Gongura Prawns',           'category': 'non_veg_pickles', 'tag': 'New',         'price': 600,  'weight': '250g', 'rating': 4.8, 'desc': 'Fresh prawns tossed in gongura masala for a tangy punch.',                'img': 'https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=600', 'weights': {'250': 600,  '500': 1200, '1000': 1800}},
    {'ProductID': '6',  'name': 'Chicken Pickle (Gongura)', 'category': 'non_veg_pickles', 'tag': 'Popular',     'price': 350,  'weight': '250g', 'rating': 4.6, 'desc': 'Classic chicken pickle infused with gongura sourness.',                   'img': 'https://images.unsplash.com/photo-1610057099431-d73a1c9d2f2f?w=600', 'weights': {'250': 350,  '500': 700,  '1000': 1050}},
    # ── VEG PICKLES ──────────────────────────────────────────────────────────
    {'ProductID': '7',  'name': 'Traditional Mango Pickle', 'category': 'veg_pickles',     'tag': 'Classic',     'price': 150,  'weight': '250g', 'rating': 4.9, 'desc': 'Sun-dried raw mango in sesame oil and mustard seeds.',                    'img': 'https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600', 'weights': {'250': 150,  '500': 280,  '1000': 500}},
    {'ProductID': '8',  'name': 'Zesty Lemon Pickle',       'category': 'veg_pickles',     'tag': 'Tangy',       'price': 120,  'weight': '250g', 'rating': 4.6, 'desc': 'Aged lemon pickle with a sharp citrusy kick.',                            'img': 'https://images.unsplash.com/photo-1587486936739-78a3a6d4a176?w=600', 'weights': {'250': 120,  '500': 220,  '1000': 400}},
    {'ProductID': '9',  'name': 'Tomato Pickle',            'category': 'veg_pickles',     'tag': 'Sweet-Spicy', 'price': 130,  'weight': '250g', 'rating': 4.5, 'desc': 'Ripe tomatoes cooked into a rich, spiced preserve.',                      'img': 'https://images.unsplash.com/photo-1558818498-28c1e002b655?w=600', 'weights': {'250': 130,  '500': 240,  '1000': 450}},
    {'ProductID': '10', 'name': 'Kakarakaya Pickle',        'category': 'veg_pickles',     'tag': 'Bitter',      'price': 130,  'weight': '250g', 'rating': 4.3, 'desc': 'Bitter gourd pickle — bold, healthy and traditionally made.',             'img': 'https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=600', 'weights': {'250': 130,  '500': 240,  '1000': 450}},
    {'ProductID': '11', 'name': 'Chintakaya Pickle',        'category': 'veg_pickles',     'tag': 'Sour',        'price': 130,  'weight': '250g', 'rating': 4.4, 'desc': 'Tender tamarind pods pickled in sesame oil and spices.',                  'img': 'https://images.unsplash.com/photo-1596591868231-05e808fd131d?w=600', 'weights': {'250': 130,  '500': 240,  '1000': 450}},
    {'ProductID': '12', 'name': 'Spicy Pandu Mirchi',       'category': 'veg_pickles',     'tag': 'Hot',         'price': 130,  'weight': '250g', 'rating': 4.7, 'desc': 'Red chilli pickle — fire in a jar for heat lovers.',                      'img': 'https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=600', 'weights': {'250': 130,  '500': 240,  '1000': 450}},
    # ── SNACKS ───────────────────────────────────────────────────────────────
    {'ProductID': '13', 'name': 'Banana Chips',             'category': 'snacks',          'tag': 'Crunchy',     'price': 300,  'weight': '250g', 'rating': 4.6, 'desc': 'Thin-sliced raw banana chips fried to golden perfection.',               'img': 'https://images.unsplash.com/photo-1621447504864-d8686e12698c?w=600', 'weights': {'250': 300,  '500': 600,  '1000': 800}},
    {'ProductID': '14', 'name': 'Crispy Aam-Papad',         'category': 'snacks',          'tag': 'Sweet',       'price': 150,  'weight': '250g', 'rating': 4.5, 'desc': 'Sun-dried mango leather — sweet, tangy, and chewy.',                     'img': 'https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=600', 'weights': {'250': 150,  '500': 300,  '1000': 600}},
    {'ProductID': '15', 'name': 'Crispy Chekka Pakodi',     'category': 'snacks',          'tag': 'Crispy',      'price': 50,   'weight': '250g', 'rating': 4.4, 'desc': 'Crunchy rice flour snack with cumin and green chilli.',                   'img': 'https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600', 'weights': {'250': 50,   '500': 100,  '1000': 200}},
    {'ProductID': '16', 'name': 'Boondhi Acchu',            'category': 'snacks',          'tag': 'Traditional', 'price': 300,  'weight': '250g', 'rating': 4.5, 'desc': 'Savoury gram flour boondi with spiced seasoning.',                        'img': 'https://images.unsplash.com/photo-1599909941439-f5d02cd69c1e?w=600', 'weights': {'250': 300,  '500': 600,  '1000': 900}},
    {'ProductID': '17', 'name': 'Chekkalu',                 'category': 'snacks',          'tag': 'Popular',     'price': 350,  'weight': '250g', 'rating': 4.7, 'desc': 'Rice crackers with sesame and chilli — an Andhra favourite.',             'img': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600', 'weights': {'250': 350,  '500': 700,  '1000': 1000}},
    {'ProductID': '18', 'name': 'Ragi Laddu',               'category': 'snacks',          'tag': 'Healthy',     'price': 350,  'weight': '250g', 'rating': 4.6, 'desc': 'Finger millet laddus sweetened with jaggery.',                           'img': 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600', 'weights': {'250': 350,  '500': 700,  '1000': 1000}},
    {'ProductID': '19', 'name': 'Dry Fruit Laddu',          'category': 'snacks',          'tag': 'Premium',     'price': 500,  'weight': '250g', 'rating': 4.9, 'desc': 'Rich laddus loaded with cashews, almonds, and dates.',                   'img': 'https://images.unsplash.com/photo-1559622214-f8a9850965bb?w=600', 'weights': {'250': 500,  '500': 1000, '1000': 1500}},
    {'ProductID': '20', 'name': 'Kara Boondi',              'category': 'snacks',          'tag': 'Spicy',       'price': 250,  'weight': '250g', 'rating': 4.5, 'desc': 'Crispy spiced boondi — perfect tea-time companion.',                      'img': 'https://images.unsplash.com/photo-1551462147-ff29053bfc14?w=600', 'weights': {'250': 250,  '500': 500,  '1000': 750}},
    {'ProductID': '21', 'name': 'Gavvalu',                  'category': 'snacks',          'tag': 'Sweet',       'price': 250,  'weight': '250g', 'rating': 4.4, 'desc': 'Shell-shaped sweet snack made from wheat and jaggery.',                   'img': 'https://images.unsplash.com/photo-1576618148400-f54bed99fcfd?w=600', 'weights': {'250': 250,  '500': 500,  '1000': 750}},
    {'ProductID': '22', 'name': 'Kaju Chikki',              'category': 'snacks',          'tag': 'Premium',     'price': 250,  'weight': '250g', 'rating': 4.8, 'desc': 'Crunchy cashew brittle made with pure jaggery.',                          'img': 'https://images.unsplash.com/photo-1614088685112-0a760b71a3c8?w=600', 'weights': {'250': 250,  '500': 500,  '1000': 750}},
    {'ProductID': '23', 'name': 'PeaNut Chikki',            'category': 'snacks',          'tag': 'Classic',     'price': 250,  'weight': '250g', 'rating': 4.6, 'desc': 'Traditional peanut brittle with jaggery and cardamom.',                   'img': 'https://images.unsplash.com/photo-1567360425618-1594206637d2?w=600', 'weights': {'250': 250,  '500': 500,  '1000': 750}},
    {'ProductID': '24', 'name': 'Rava Laddu',               'category': 'snacks',          'tag': 'Festive',     'price': 250,  'weight': '250g', 'rating': 4.5, 'desc': 'Semolina laddus with coconut, ghee, and cardamom.',                       'img': 'https://images.unsplash.com/photo-1605197161470-5d1a5b4a43b0?w=600', 'weights': {'250': 250,  '500': 500,  '1000': 750}},
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
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/non_veg_pickles')
@login_required
def non_veg_pickles():
    return render_template('non_veg_pickles.html', products=[p for p in PRODUCTS if p['category'] == 'non_veg_pickles'])

@app.route('/veg_pickles')
@login_required
def veg_pickles():
    return render_template('veg_pickles.html', products=[p for p in PRODUCTS if p['category'] == 'veg_pickles'])

@app.route('/snacks')
@login_required
def snacks():
    return render_template('snacks.html', products=[p for p in PRODUCTS if p['category'] == 'snacks'])

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact us.html')

# ============================================================
# AUTH ROUTES (HTML Form-based)
# ============================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return render_template('login.html', error='Username and password are required.')
        try:
            result = users_table.scan(
                FilterExpression='username = :u',
                ExpressionAttributeValues={':u': username}
            )
            items = result.get('Items', [])
            if not items:
                return render_template('login.html', error='User not found. Please sign up.')
            user = items[0]
            if not check_password_hash(user.get('password', ''), password):
                return render_template('login.html', error='Incorrect password.')
            session.permanent   = True
            session['logged_in'] = True
            session['username']  = user.get('username', username)
            session['name']      = user.get('name', username)
            session['UserID']    = user['UserID']
            session['email']     = user.get('email', '')
            session['cart']      = []
            return redirect(url_for('home'))
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            return render_template('login.html', error=f'Login failed: {str(e)}')
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email',    '').strip()
        phone    = request.form.get('phone',    '').strip()
        password = request.form.get('password', '')

        if not all([username, email, password]):
            return render_template('signup.html', error='All fields are required.')
        try:
            # Check username
            r1 = users_table.scan(FilterExpression='username = :u', ExpressionAttributeValues={':u': username})
            if r1.get('Items'):
                return render_template('signup.html', error='Username already taken.')
            # Check email
            r2 = users_table.scan(FilterExpression='email = :e', ExpressionAttributeValues={':e': email})
            if r2.get('Items'):
                return render_template('signup.html', error='Email already registered.')

            user_id = str(uuid.uuid4())
            users_table.put_item(Item={
                'UserID':     user_id,    # PK
                'username':   username,
                'name':       username,
                'email':      email,
                'phone':      phone,
                'password':   generate_password_hash(password),
                'created_at': datetime.now().isoformat()
            })
            return redirect(url_for('login'))
        except Exception as e:
            app.logger.error(f"Signup error: {e}")
            return render_template('signup.html', error=f'Registration failed: {str(e)}')
    return render_template('signup.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ============================================================
# CHECKOUT
# ============================================================
@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        name           = request.form.get('name',         '').strip()
        address        = request.form.get('address',      '').strip()
        phone          = request.form.get('phone',        '').strip()
        payment_method = request.form.get('payment',      '').strip()
        cart_data      = request.form.get('cart_data',    '[]')
        total_amount   = request.form.get('total_amount', '0')

        if not all([name, address, phone, payment_method]):
            return render_template('checkout.html', error='All fields are required.')
        if not phone.isdigit() or len(phone) != 10:
            return render_template('checkout.html', error='Phone must be 10 digits.')
        try:
            cart_items   = json.loads(cart_data)
            total_amount = Decimal(str(total_amount))
        except Exception:
            return render_template('checkout.html', error='Invalid cart data.')
        if not cart_items:
            return render_template('checkout.html', error='Cart is empty.')
        try:
            orders_table.put_item(Item={
                'OrderID':        str(uuid.uuid4()),  # PK
                'UserID':         session.get('UserID', ''),
                'username':       session.get('username', 'Guest'),
                'name':           name,
                'address':        address,
                'phone':          phone,
                'items':          cart_items,
                'total_amount':   str(total_amount),
                'payment_method': payment_method,
                'status':         'placed',
                'timestamp':      datetime.now().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Checkout error: {e}")
            return render_template('checkout.html', error=f'Failed to save order: {str(e)}')
        return redirect(url_for('success'))
    return render_template('checkout.html')


@app.route('/success')
@app.route('/sucess')
def success():
    return render_template('sucess.html')


# ============================================================
# JSON API ENDPOINTS
# ============================================================

@app.route('/api/auth/status')
def api_auth_status():
    if session.get('logged_in'):
        return jsonify({
            'authenticated': True,
            'user': {
                'UserID':   session.get('UserID'),
                'username': session.get('username'),
                'name':     session.get('name', session.get('username')),
                'email':    session.get('email', '')
            }
        })
    return jsonify({'authenticated': False, 'user': None})


@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data     = request.get_json(silent=True) or {}
    email    = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    try:
        result = users_table.scan(
            FilterExpression='email = :e',
            ExpressionAttributeValues={':e': email}
        )
        items = result.get('Items', [])
        if not items:
            return jsonify({'error': 'No account found with that email. Please sign up.'}), 401
        user = items[0]
        if not check_password_hash(user.get('password', ''), password):
            return jsonify({'error': 'Incorrect password.'}), 401

        display_name = user.get('name', user.get('username', email.split('@')[0]))
        session.permanent   = True
        session['logged_in'] = True
        session['username']  = user.get('username', display_name)
        session['name']      = display_name
        session['UserID']    = user['UserID']
        session['email']     = user.get('email', '')
        session['cart']      = []
        return jsonify({
            'message': 'Signed in.',
            'user': {'UserID': user['UserID'], 'name': display_name, 'email': session['email']}
        })
    except Exception as e:
        app.logger.error(f"API login error: {e}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500


@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data     = request.get_json(silent=True) or {}
    name     = data.get('name',     '').strip()
    email    = data.get('email',    '').strip()
    phone    = data.get('phone',    '').strip()
    password = data.get('password', '')

    if not all([name, email, password]):
        return jsonify({'error': 'Name, email and password are required.'}), 400
    try:
        result = users_table.scan(
            FilterExpression='email = :e',
            ExpressionAttributeValues={':e': email}
        )
        if result.get('Items'):
            return jsonify({'error': 'Account with that email already exists.'}), 409

        user_id = str(uuid.uuid4())
        users_table.put_item(Item={
            'UserID':     user_id,    # PK
            'name':       name,
            'username':   name,
            'email':      email,
            'phone':      phone,
            'password':   generate_password_hash(password),
            'created_at': datetime.now().isoformat()
        })
        session.permanent   = True
        session['logged_in'] = True
        session['username']  = name
        session['name']      = name
        session['UserID']    = user_id
        session['email']     = email
        session['cart']      = []
        return jsonify({
            'message': 'Account created!',
            'user': {'UserID': user_id, 'name': name, 'email': email}
        }), 201
    except Exception as e:
        app.logger.error(f"API register error: {e}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': 'Signed out.'})


@app.route('/api/products')
def api_products():
    category = request.args.get('category', '').strip().lower()
    search   = request.args.get('search',   '').strip().lower()
    result   = PRODUCTS[:]
    if category and category not in ('all', ''):
        cat_map = {'pickles': ['non_veg_pickles', 'veg_pickles'], 'snacks': ['snacks']}
        allowed = cat_map.get(category, [category])
        result = [p for p in result if p['category'] in allowed]
    if search:
        result = [p for p in result if search in p['name'].lower()]
    output = [{**p, 'product_id': p['ProductID']} for p in result]
    return jsonify({'products': output, 'total': len(output)})


@app.route('/api/recommendations')
def api_recommendations():
    import random
    sample = random.sample(PRODUCTS, min(4, len(PRODUCTS)))
    return jsonify({'recommendations': [{**p, 'product_id': p['ProductID']} for p in sample]})


@app.route('/api/orders', methods=['POST'])
@login_required
def api_place_order():
    data           = request.get_json(silent=True) or {}
    items          = data.get('items', [])
    payment_method = data.get('payment_method', 'cod')
    shipping       = data.get('shipping_address', {})

    if not items:
        return jsonify({'error': 'Cart is empty.'}), 400

    enriched = []
    total    = Decimal('0')
    for item in items:
        product = get_product_by_id(str(item.get('product_id', '')))
        if not product:
            return jsonify({'error': f"Product {item.get('product_id')} not found."}), 400
        qty   = int(item.get('quantity', 1))
        price = Decimal(str(product['price']))
        enriched.append({'ProductID': product['ProductID'], 'name': product['name'], 'price': str(price), 'quantity': qty, 'subtotal': str(price * qty)})
        total += price * qty

    order_id = str(uuid.uuid4())
    try:
        orders_table.put_item(Item={
            'OrderID':          order_id,   # PK
            'UserID':           session.get('UserID', ''),
            'username':         session.get('username', ''),
            'items':            enriched,
            'total_amount':     str(total),
            'payment_method':   payment_method,
            'shipping_address': shipping,
            'status':           'placed',
            'timestamp':        datetime.now().isoformat()
        })
    except Exception as e:
        app.logger.error(f"API order error: {e}")
        return jsonify({'error': f'Failed to place order: {str(e)}'}), 500

    return jsonify({'message': 'Order placed!', 'order': {'order_id': order_id, 'total_amount': str(total), 'status': 'placed'}}), 201


@app.route('/api/orders', methods=['GET'])
@login_required
def api_get_orders():
    try:
        result = orders_table.scan(FilterExpression='UserID = :u', ExpressionAttributeValues={':u': session.get('UserID', '')})
        return jsonify({'orders': safe_json(result.get('Items', []))})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch orders: {str(e)}'}), 500


@app.route('/api/favorites', methods=['GET'])
@login_required
def api_get_favorites():
    return jsonify({'favorites': session.get('favorites', [])})

@app.route('/api/favorites', methods=['POST'])
@login_required
def api_add_favorite():
    data = request.get_json(silent=True) or {}
    pid  = str(data.get('product_id', ''))
    favs = session.get('favorites', [])
    if pid not in favs:
        favs.append(pid)
        session['favorites'] = favs
    return jsonify({'message': 'Added.', 'favorites': favs})

@app.route('/api/favorites/<product_id>', methods=['DELETE'])
@login_required
def api_remove_favorite(product_id):
    session['favorites'] = [f for f in session.get('favorites', []) if f != product_id]
    return jsonify({'message': 'Removed.', 'favorites': session['favorites']})


@app.route('/health')
def health():
    try:
        users_table.load()
        db = 'connected'
    except Exception as e:
        db = f'error: {e}'
    return jsonify({'status': 'ok', 'dynamodb': db, 'timestamp': datetime.now().isoformat()})


# ============================================================
# RUN
# ============================================================
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)