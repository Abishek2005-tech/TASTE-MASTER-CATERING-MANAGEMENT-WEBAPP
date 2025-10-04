# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
import yaml

app = Flask(__name__)

# --- Database Configuration ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'catering_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 'your_super_secret_key_12345'

mysql = MySQL(app)

# ======================================================
# ##          1. Main & User Authentication Routes      ##
# ======================================================

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM foods")
    food_items = cur.fetchall()
    cur.close()
    welcome_message = "What would you like to order today?"
    if 'loggedin' in session:
        welcome_message = f"Welcome, {session['name']}! What are you craving?"
    return render_template('index.html', food_items=food_items, welcome_message=welcome_message)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE phone = %s", [phone])
        account = cur.fetchone()
        if account:
            flash("An account with this phone number already exists!", "danger")
            return redirect(url_for('register'))
        # NEW: Sets the default role to 'user'
        cur.execute("INSERT INTO users(name, phone, password, role) VALUES (%s, %s, %s, 'user')", (name, phone, hashed_password))
        mysql.connection.commit()
        cur.close()
        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form['phone']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE phone = %s", [phone])
        account = cur.fetchone()
        cur.close()
        if account and check_password_hash(account['password'], password_candidate):
            session['loggedin'] = True
            session['id'] = account['id']
            session['name'] = account['name']
            # NEW: Check the 'role' column from the database
            session['is_admin'] = True if account['role'] == 'admin' else False
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Incorrect phone number or password!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# ======================================================
# ##          2. Ordering Flow & History Routes         ##
# ======================================================
# (These routes remain unchanged)
@app.route('/order_summary/<int:food_id>')
def order_summary(food_id):
    # ... (existing code)
    if 'loggedin' not in session:
        flash("Please log in to place an order.", "warning")
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM foods WHERE id = %s", [food_id])
    food_item = cur.fetchone()
    cur.close()
    if not food_item:
        flash("Food item not found!", "danger")
        return redirect(url_for('index'))
    return render_template('order_summary.html', item=food_item)

@app.route('/checkout', methods=['POST'])
def checkout():
    # ... (existing code)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    try:
        food_id = request.form['food_id']
        quantity = int(request.form['quantity'])
        delivery_option = request.form['delivery_option']
        delivery_date = request.form['delivery_date']
        delivery_time = request.form['delivery_time']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM foods WHERE id = %s", [food_id])
        food = cur.fetchone()
        if not food:
            flash("Could not find the selected food item. Please try again.", "danger")
            return redirect(url_for('index'))
        subtotal = food['price_per_unit'] * quantity
        delivery_fee = Decimal('50.00') if delivery_option == 'delivery' else Decimal('0.00')
        total_amount = subtotal + delivery_fee
        cur.execute("INSERT INTO orders(user_id, total_amount, delivery_date, delivery_time, delivery_option, payment_method) VALUES (%s, %s, %s, %s, %s, %s)", (session['id'], total_amount, delivery_date, delivery_time, delivery_option, 'Simulated Payment'))
        mysql.connection.commit()
        new_order_id = cur.lastrowid
        cur.close()
        return render_template('order_success.html', order_id=new_order_id)
    except Exception as e:
        print(f"An error occurred in checkout: {e}")
        flash("An unexpected server error occurred. Please try again.", "danger")
        return redirect(url_for('index'))

@app.route('/my_orders')
def my_orders():
    # ... (existing code)
    if 'loggedin' not in session:
        flash("Please log in to view your orders.", "warning")
        return redirect(url_for('login'))
    user_id = session['id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY order_date DESC", [user_id])
    orders = cur.fetchall()
    cur.close()
    return render_template('my_orders.html', orders=orders)


# ======================================================
# ##          3. Admin Routes (UPDATED & NEW)           ##
# ======================================================

# Wrapper function to check if user is admin
from functools import wraps
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('loggedin') or not session.get('is_admin'):
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Main dashboard for the admin."""
    return render_template('admin_dashboard.html')

@app.route('/admin/requests')
@admin_required
def admin_requests():
    """Admin page to view pending custom food requests."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT cr.id, u.name, cr.food_name, cr.quantity, cr.delivery_date, cr.delivery_time FROM custom_requests cr JOIN users u ON cr.user_id = u.id WHERE cr.status = 'pending' ORDER BY cr.id DESC")
    requests = cur.fetchall()
    cur.close()
    return render_template('admin_requests.html', requests=requests)

@app.route('/admin/approve/<int:request_id>')
@admin_required
def approve_request(request_id):
    """Admin action to approve a custom request."""
    cur = mysql.connection.cursor()
    cur.execute("UPDATE custom_requests SET status = 'approved' WHERE id = %s", [request_id])
    mysql.connection.commit()
    cur.close()
    flash("Request has been approved!", "success")
    return redirect(url_for('admin_requests'))

# --- NEW FOOD MANAGEMENT ROUTES ---

@app.route('/admin/foods')
@admin_required
def admin_foods():
    """Displays all food items for management."""
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM foods ORDER BY id DESC")
    foods = cur.fetchall()
    cur.close()
    return render_template('admin_foods.html', foods=foods)

@app.route('/admin/add_food', methods=['GET', 'POST'])
@admin_required
def add_food():
    """Handles adding a new food item."""
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO foods(name, description, price_per_unit, image_url) VALUES (%s, %s, %s, %s)", (name, description, price, image_url))
        mysql.connection.commit()
        cur.close()
        flash(f"Food item '{name}' has been added successfully!", "success")
        return redirect(url_for('admin_foods'))
    return render_template('add_food.html')

@app.route('/admin/edit_food/<int:food_id>', methods=['GET', 'POST'])
@admin_required
def edit_food(food_id):
    """Handles editing an existing food item."""
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        cur.execute("UPDATE foods SET name = %s, description = %s, price_per_unit = %s, image_url = %s WHERE id = %s", (name, description, price, image_url, food_id))
        mysql.connection.commit()
        cur.close()
        flash(f"Food item '{name}' has been updated successfully!", "success")
        return redirect(url_for('admin_foods'))
    
    # GET request: fetch the food item and show the edit form
    cur.execute("SELECT * FROM foods WHERE id = %s", [food_id])
    food = cur.fetchone()
    cur.close()
    return render_template('edit_food.html', food=food)

@app.route('/admin/delete_food/<int:food_id>')
@admin_required
def delete_food(food_id):
    """Handles deleting a food item."""
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM foods WHERE id = %s", [food_id])
    mysql.connection.commit()
    cur.close()
    flash("Food item has been deleted.", "success")
    return redirect(url_for('admin_foods'))

# ======================================================
# ##          4. Custom Order Route (User-facing)       ##
# ======================================================
@app.route('/custom_order', methods=['GET', 'POST'])
def custom_order():
    # ... (existing code)
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO custom_requests(user_id, food_name, quantity, delivery_date, delivery_time) VALUES (%s, %s, %s, %s, %s)", (session['id'], request.form['food_name'], request.form['quantity'], request.form['delivery_date'], request.form['delivery_time']))
        mysql.connection.commit()
        cur.close()
        flash("Your custom food request has been sent for approval!", "info")
        return redirect(url_for('index'))
    return render_template('custom_order.html')

# ======================================================
# ##          5. Run the Application                    ##
# ======================================================

if __name__ == '__main__':
    app.run(debug=True)