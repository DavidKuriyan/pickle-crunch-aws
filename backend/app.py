"""
HomeMade Pickles & Snacks - Flask Backend
AWS Cloud-Enabled E-Commerce Platform
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import os
from datetime import datetime, timedelta
import uuid
import hashlib
import secrets

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # Enable in production with HTTPS
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# AWS Configuration
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
DYNAMODB_ENDPOINT = os.environ.get('DYNAMODB_ENDPOINT', None)  # For local testing

# Initialize DynamoDB
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    endpoint_url=DYNAMODB_ENDPOINT
)

# DynamoDB Tables
users_table = dynamodb.Table('HomeMadeUsers')
products_table = dynamodb.Table('HomeMadeProducts')
orders_table = dynamodb.Table('HomeMadeOrders')
inventory_table = dynamodb.Table('HomeMadeInventory')
subscriptions_table = dynamodb.Table('HomeMadeSubscriptions')


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def decimal_to_float(obj):
    """Convert DynamoDB Decimal to float for JSON serialization"""
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    return obj


def login_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()

        # Validation
        if not all([email, password, name]):
            return jsonify({'error': 'Email, password, and name are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        # Check if user already exists
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' in response:
                return jsonify({'error': 'User already exists'}), 409
        except Exception as e:
            print(f"Error checking existing user: {e}")

        # Create user
        user_id = str(uuid.uuid4())
        user_data = {
            'user_id': user_id,
            'email': email,
            'password': hash_password(password),
            'name': name,
            'phone': phone,
            'created_at': datetime.now().isoformat(),
            'favorites': [],
            'addresses': []
        }

        users_table.put_item(Item=user_data)

        # Set session
        session['user_id'] = user_id
        session['email'] = email
        session['name'] = name
        session.permanent = True

        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'user_id': user_id,
                'email': email,
                'name': name
            }
        }), 201

    except Exception as e:
        print(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        # Get user from DynamoDB
        response = users_table.get_item(Key={'email': email})
        
        if 'Item' not in response:
            return jsonify({'error': 'Invalid email or password'}), 401

        user = response['Item']

        # Verify password
        if user['password'] != hash_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401

        # Set session
        session['user_id'] = user['user_id']
        session['email'] = user['email']
        session['name'] = user['name']
        session.permanent = True

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'user_id': user['user_id'],
                'email': user['email'],
                'name': user['name']
            }
        }), 200

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """User logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'user_id': session['user_id'],
                'email': session['email'],
                'name': session['name']
            }
        }), 200
    return jsonify({'authenticated': False}), 200


# ============================================================================
# PRODUCT ROUTES
# ============================================================================

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional category filter"""
    try:
        category = request.args.get('category')
        
        if category and category != 'all':
            response = products_table.scan(
                FilterExpression=Attr('category').eq(category)
            )
        else:
            response = products_table.scan()

        products = decimal_to_float(response.get('Items', []))
        
        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        }), 200

    except Exception as e:
        print(f"Error fetching products: {e}")
        return jsonify({'error': 'Failed to fetch products'}), 500


@app.route('/api/products/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    try:
        response = products_table.get_item(Key={'product_id': product_id})
        
        if 'Item' not in response:
            return jsonify({'error': 'Product not found'}), 404

        product = decimal_to_float(response['Item'])
        
        return jsonify({
            'success': True,
            'product': product
        }), 200

    except Exception as e:
        print(f"Error fetching product: {e}")
        return jsonify({'error': 'Failed to fetch product'}), 500


# ============================================================================
# INVENTORY ROUTES
# ============================================================================

@app.route('/api/inventory/<product_id>', methods=['GET'])
def get_inventory(product_id):
    """Get inventory for a product"""
    try:
        response = inventory_table.get_item(Key={'product_id': product_id})
        
        if 'Item' not in response:
            return jsonify({'error': 'Inventory not found'}), 404

        inventory = decimal_to_float(response['Item'])
        
        return jsonify({
            'success': True,
            'inventory': inventory
        }), 200

    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return jsonify({'error': 'Failed to fetch inventory'}), 500


def update_inventory(product_id, quantity_change):
    """Update inventory levels (internal function)"""
    try:
        response = inventory_table.update_item(
            Key={'product_id': product_id},
            UpdateExpression='SET stock = stock + :change, last_updated = :timestamp',
            ExpressionAttributeValues={
                ':change': quantity_change,
                ':timestamp': datetime.now().isoformat()
            },
            ReturnValues='ALL_NEW'
        )
        return response['Attributes']
    except Exception as e:
        print(f"Error updating inventory: {e}")
        raise


# ============================================================================
# ORDER ROUTES
# ============================================================================

@app.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    """Create a new order"""
    try:
        data = request.json
        cart_items = data.get('items', [])
        
        if not cart_items:
            return jsonify({'error': 'Cart is empty'}), 400

        # Calculate total and validate inventory
        total_amount = Decimal('0')
        order_items = []

        for item in cart_items:
            product_id = item['product_id']
            quantity = int(item['quantity'])

            # Get product details
            product_response = products_table.get_item(Key={'product_id': product_id})
            if 'Item' not in product_response:
                return jsonify({'error': f'Product {product_id} not found'}), 404

            product = product_response['Item']

            # Check inventory
            inventory_response = inventory_table.get_item(Key={'product_id': product_id})
            if 'Item' not in inventory_response:
                return jsonify({'error': f'Inventory not found for {product_id}'}), 404

            inventory = inventory_response['Item']
            if inventory['stock'] < quantity:
                return jsonify({'error': f'Insufficient stock for {product["name"]}'}), 400

            # Calculate item total
            item_total = Decimal(str(product['price'])) * Decimal(str(quantity))
            total_amount += item_total

            order_items.append({
                'product_id': product_id,
                'name': product['name'],
                'price': product['price'],
                'quantity': quantity,
                'subtotal': float(item_total)
            })

        # Create order
        order_id = str(uuid.uuid4())
        order_data = {
            'order_id': order_id,
            'user_id': session['user_id'],
            'items': order_items,
            'total_amount': total_amount,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'shipping_address': data.get('shipping_address', {}),
            'payment_method': data.get('payment_method', 'cod')
        }

        orders_table.put_item(Item=order_data)

        # Update inventory for each item
        for item in cart_items:
            update_inventory(item['product_id'], -int(item['quantity']))

        return jsonify({
            'success': True,
            'message': 'Order placed successfully',
            'order': {
                'order_id': order_id,
                'total_amount': float(total_amount),
                'status': 'pending'
            }
        }), 201

    except Exception as e:
        print(f"Error creating order: {e}")
        return jsonify({'error': 'Failed to create order'}), 500


@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    """Get all orders for the logged-in user"""
    try:
        response = orders_table.scan(
            FilterExpression=Attr('user_id').eq(session['user_id'])
        )

        orders = decimal_to_float(response.get('Items', []))
        
        # Sort by created_at descending
        orders.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }), 200

    except Exception as e:
        print(f"Error fetching orders: {e}")
        return jsonify({'error': 'Failed to fetch orders'}), 500


@app.route('/api/orders/<order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """Get a specific order"""
    try:
        response = orders_table.get_item(Key={'order_id': order_id})
        
        if 'Item' not in response:
            return jsonify({'error': 'Order not found'}), 404

        order = response['Item']

        # Verify order belongs to user
        if order['user_id'] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify({
            'success': True,
            'order': decimal_to_float(order)
        }), 200

    except Exception as e:
        print(f"Error fetching order: {e}")
        return jsonify({'error': 'Failed to fetch order'}), 500


# ============================================================================
# SUBSCRIPTION ROUTES
# ============================================================================

@app.route('/api/subscriptions', methods=['POST'])
@login_required
def create_subscription():
    """Create a subscription plan"""
    try:
        data = request.json
        plan_type = data.get('plan_type')  # weekly, monthly
        products = data.get('products', [])

        if not plan_type or not products:
            return jsonify({'error': 'Plan type and products are required'}), 400

        subscription_id = str(uuid.uuid4())
        subscription_data = {
            'subscription_id': subscription_id,
            'user_id': session['user_id'],
            'plan_type': plan_type,
            'products': products,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'next_delivery': (datetime.now() + timedelta(days=7 if plan_type == 'weekly' else 30)).isoformat()
        }

        subscriptions_table.put_item(Item=subscription_data)

        return jsonify({
            'success': True,
            'message': 'Subscription created successfully',
            'subscription': decimal_to_float(subscription_data)
        }), 201

    except Exception as e:
        print(f"Error creating subscription: {e}")
        return jsonify({'error': 'Failed to create subscription'}), 500


@app.route('/api/subscriptions', methods=['GET'])
@login_required
def get_subscriptions():
    """Get all subscriptions for the logged-in user"""
    try:
        response = subscriptions_table.scan(
            FilterExpression=Attr('user_id').eq(session['user_id'])
        )

        subscriptions = decimal_to_float(response.get('Items', []))

        return jsonify({
            'success': True,
            'subscriptions': subscriptions,
            'count': len(subscriptions)
        }), 200

    except Exception as e:
        print(f"Error fetching subscriptions: {e}")
        return jsonify({'error': 'Failed to fetch subscriptions'}), 500


@app.route('/api/subscriptions/<subscription_id>', methods=['DELETE'])
@login_required
def cancel_subscription(subscription_id):
    """Cancel a subscription"""
    try:
        response = subscriptions_table.get_item(Key={'subscription_id': subscription_id})
        
        if 'Item' not in response:
            return jsonify({'error': 'Subscription not found'}), 404

        subscription = response['Item']

        # Verify subscription belongs to user
        if subscription['user_id'] != session['user_id']:
            return jsonify({'error': 'Unauthorized'}), 403

        # Update status to cancelled
        subscriptions_table.update_item(
            Key={'subscription_id': subscription_id},
            UpdateExpression='SET #status = :status',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':status': 'cancelled'}
        )

        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully'
        }), 200

    except Exception as e:
        print(f"Error cancelling subscription: {e}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500


# ============================================================================
# RECOMMENDATIONS
# ============================================================================

@app.route('/api/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    """Get personalized product recommendations"""
    try:
        # Get user's order history
        orders_response = orders_table.scan(
            FilterExpression=Attr('user_id').eq(session['user_id'])
        )
        
        orders = orders_response.get('Items', [])
        
        # Extract purchased product categories
        purchased_categories = set()
        for order in orders:
            for item in order.get('items', []):
                product_response = products_table.get_item(Key={'product_id': item['product_id']})
                if 'Item' in product_response:
                    purchased_categories.add(product_response['Item'].get('category'))

        # Get products from purchased categories that user hasn't ordered
        purchased_product_ids = set()
        for order in orders:
            for item in order.get('items', []):
                purchased_product_ids.add(item['product_id'])

        # Fetch recommended products
        recommendations = []
        if purchased_categories:
            for category in purchased_categories:
                products_response = products_table.scan(
                    FilterExpression=Attr('category').eq(category)
                )
                for product in products_response.get('Items', []):
                    if product['product_id'] not in purchased_product_ids:
                        recommendations.append(product)
        
        # If no order history, recommend popular items (high ratings)
        if not recommendations:
            all_products = products_table.scan()
            recommendations = sorted(
                all_products.get('Items', []),
                key=lambda x: float(x.get('rating', 0)),
                reverse=True
            )[:6]

        return jsonify({
            'success': True,
            'recommendations': decimal_to_float(recommendations[:6])
        }), 200

    except Exception as e:
        print(f"Error fetching recommendations: {e}")
        return jsonify({'error': 'Failed to fetch recommendations'}), 500


# ============================================================================
# FAVORITES
# ============================================================================

@app.route('/api/favorites', methods=['POST'])
@login_required
def add_favorite():
    """Add product to favorites"""
    try:
        data = request.json
        product_id = data.get('product_id')

        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400

        # Update user's favorites
        users_table.update_item(
            Key={'email': session['email']},
            UpdateExpression='SET favorites = list_append(if_not_exists(favorites, :empty_list), :product)',
            ExpressionAttributeValues={
                ':product': [product_id],
                ':empty_list': []
            }
        )

        return jsonify({
            'success': True,
            'message': 'Added to favorites'
        }), 200

    except Exception as e:
        print(f"Error adding favorite: {e}")
        return jsonify({'error': 'Failed to add favorite'}), 500


@app.route('/api/favorites/<product_id>', methods=['DELETE'])
@login_required
def remove_favorite(product_id):
    """Remove product from favorites"""
    try:
        # Get current favorites
        response = users_table.get_item(Key={'email': session['email']})
        user = response.get('Item', {})
        favorites = user.get('favorites', [])

        # Remove product_id
        if product_id in favorites:
            favorites.remove(product_id)
            
            users_table.update_item(
                Key={'email': session['email']},
                UpdateExpression='SET favorites = :favorites',
                ExpressionAttributeValues={':favorites': favorites}
            )

        return jsonify({
            'success': True,
            'message': 'Removed from favorites'
        }), 200

    except Exception as e:
        print(f"Error removing favorite: {e}")
        return jsonify({'error': 'Failed to remove favorite'}), 500


# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.route('/')
def index():
    """Homepage"""
    return render_template('index.html')


@app.route('/products')
def products():
    """Products page"""
    return render_template('products.html')


@app.route('/cart')
def cart():
    """Shopping cart page"""
    return render_template('cart.html')


@app.route('/account')
def account():
    """User account page"""
    return render_template('account.html')


@app.route('/subscriptions')
def subscriptions():
    """Subscriptions page"""
    return render_template('subscriptions.html')


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Development server
    app.run(host='0.0.0.0', port=5000, debug=True)
