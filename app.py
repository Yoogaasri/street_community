from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'street_community_db'
app.config['UPLOAD_FOLDER'] = 'uploads'

mysql = MySQL(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            cur = mysql.connection.cursor()
            cur.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]  # Store user_id in the session
                return redirect(url_for('user_dashboard'))
            else:
                flash('Login failed. Check your email and password.', 'danger')

        else:
            flash('Email and password are required.', 'danger')

    return render_template('login.html')




@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin_username = 'admin'
        admin_password = 'admin'

        if username == admin_username and password == admin_password:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template('admin_login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        age = request.form.get('age')
        gender = request.form.get('gender')

        id_proof = request.files.get('id_proof')

        if id_proof and id_proof.filename == '':
            flash('No file selected for ID Proof', 'danger')
            return redirect(url_for('register'))

        street_id = request.form.get('street_id')

        if not street_id:
            flash('Street ID is required', 'danger')
            return redirect(url_for('register'))

        user_type = request.form.get('user_type')
        password = request.form.get('password')

        hashed_password = generate_password_hash(password)

        if id_proof:
            id_proof_path = os.path.join('uploads', id_proof.filename)
            id_proof.save(id_proof_path)

        try:
            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT street_name FROM streets WHERE id = %s", (street_id,))
            street_name_row = cur.fetchone()
            street_name = street_name_row[0] if street_name_row else None

            cur.execute("""
                INSERT INTO users (name, phone, email, age, gender, id_proof, street_id, user_type, password, street_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, phone, email, age, gender, id_proof.filename, street_id, user_type, hashed_password, street_name))
            mysql.connection.commit()
            cur.close()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error during registration: {str(e)}', 'danger')

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, street_name FROM streets")
        streets = cur.fetchall()
        cur.close()
    except Exception as e:
        streets = []
        flash(f'Error fetching streets: {str(e)}', 'danger')

    return render_template('register.html', streets=streets)


@app.route('/manage_streets', methods=['GET'])
def manage_streets():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM streets")
    streets = cur.fetchall()
    cur.close()
    return render_template('manage_streets.html', streets=streets)


@app.route('/manage_maids', methods=['GET'])
def manage_maids():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT maids.id, maids.name, maids.phone, maids.email, streets.name 
        FROM maids 
        LEFT JOIN streets ON maids.street_id = streets.id
    """)
    maids = cur.fetchall()
    cur.close()
    return render_template('manage_maids.html', maids=maids)


@app.route('/manage_shops', methods=['GET'])
def manage_shops():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT shops.id, shops.name, shops.category, streets.name 
        FROM shops 
        LEFT JOIN streets ON shops.street_id = streets.id
    """)
    shops = cur.fetchall()
    cur.close()
    return render_template('manage_shops.html', shops=shops)


@app.route('/manage_grievances', methods=['GET'])
def manage_grievances():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM grievances")
    grievances = cur.fetchall()
    cur.close()
    return render_template('manage_grievances.html', grievances=grievances)


@app.route('/manage_utilities', methods=['GET', 'POST'])
def manage_utilities():
    if request.method == 'POST':
        utility_type = request.form['utility_type']
        status = request.form['status']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO utilities (type, status) VALUES (%s, %s)", (utility_type, status))
        mysql.connection.commit()
        cur.close()
        flash('Utility added successfully!', 'success')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM utilities")
    utilities = cur.fetchall()
    cur.close()
    return render_template('manage_utilities.html', utilities=utilities)


@app.route('/add_street', methods=['GET', 'POST'])
def add_street():
    if request.method == 'POST':
        street_name = request.form['name']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO streets (name) VALUES (%s)", (street_name,))
        mysql.connection.commit()
        cur.close()
        flash('Street added successfully!', 'success')
        return redirect(url_for('manage_streets'))
    return render_template('add_street.html')


@app.route('/delete_street/<int:street_id>', methods=['POST'])
def delete_street(street_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM streets WHERE id = %s", (street_id,))
    mysql.connection.commit()
    cur.close()
    flash('Street deleted successfully!', 'success')
    return redirect(url_for('manage_streets'))


@app.route('/delete_maid/<int:maid_id>', methods=['POST'])
def delete_maid(maid_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM maids WHERE id = %s", (maid_id,))
    mysql.connection.commit()
    cur.close()
    flash('Maid deleted successfully!', 'success')
    return redirect(url_for('manage_maids'))


@app.route('/delete_shop/<int:shop_id>', methods=['POST'])
def delete_shop(shop_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM shops WHERE id = %s", (shop_id,))
    mysql.connection.commit()
    cur.close()
    flash('Shop deleted successfully!', 'success')
    return redirect(url_for('manage_shops'))


@app.route('/resolve_grievance/<int:grievance_id>', methods=['POST'])
def resolve_grievance(grievance_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE grievances SET status = 'Resolved' WHERE id = %s", (grievance_id,))
    mysql.connection.commit()
    cur.close()
    flash('Grievance resolved successfully!', 'success')
    return redirect(url_for('manage_grievances'))


@app.route('/delete_utility/<int:utility_id>', methods=['POST'])
def delete_utility(utility_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM utilities WHERE id = %s", (utility_id,))
    mysql.connection.commit()
    cur.close()
    flash('Utility deleted successfully!', 'success')
    return redirect(url_for('manage_utilities'))


@app.route('/add_maid', methods=['GET', 'POST'])
def add_maid():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        street_id = request.form['street_id']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO maids (name, phone, email, street_id) VALUES (%s, %s, %s, %s)",
                    (name, phone, email, street_id))
        mysql.connection.commit()
        cur.close()
        flash('Maid added successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM streets")
    streets = cur.fetchall()
    cur.close()
    return render_template('add_maid.html', streets=streets)




@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.route('/logout_usr')
def logout_user():
    session.pop('admin', None)
    return redirect(url_for('login'))


@app.route('/verify_users')
def verify_users():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, name, email, id_proof, verified FROM users")
    users = cur.fetchall()
    cur.close()
    return render_template('verify_users.html', users=users)


@app.route('/verify_user/<int:user_id>')
def verify_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET verified = TRUE WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cur.close()
    flash('User verified successfully!', 'success')
    return redirect(url_for('verify_users'))


@app.route('/maid_requests')
def maid_requests():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT r.id, u.name, r.status 
        FROM maid_requests r 
        JOIN users u ON r.user_id = u.id
    """)
    requests = cur.fetchall()
    cur.close()
    return render_template('maid_requests.html', requests=requests)


@app.route('/verify_maid_request/<int:request_id>', methods=['POST'])
def verify_maid_request(request_id):
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE maid_requests SET status = 'verified' WHERE id = %s", (request_id,))
    mysql.connection.commit()
    cur.close()
    flash('Maid job request verified!', 'success')
    return redirect(url_for('maid_requests'))


@app.route('/create_grievance', methods=['GET', 'POST'])
def create_grievance():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        street_id = request.form['street']
        user_id = session.get('user_id')

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO grievances(title, description, user_id, street_id) VALUES(%s, %s, %s, %s)",
                    (title, description, user_id, street_id))
        mysql.connection.commit()
        cur.close()

        flash('Grievance submitted successfully!', 'success')
        return redirect(url_for('user_dashboard'))

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, street_name FROM streets")
    streets = cur.fetchall()
    cur.close()

    return render_template('create_grievance.html', streets=streets)


@app.route('/search_shops', methods=['GET'])
def search_shops():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, street_name FROM streets")
    streets = cur.fetchall()
    cur.close()

    street_id = request.args.get('street')
    shops = []

    if street_id:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT id, name, category, shop_image, shop_map_url 
            FROM shops 
            WHERE street_id = %s
        """, (street_id,))
        shops = cur.fetchall()
        cur.close()

    return render_template('search_shops.html', streets=streets, shops=shops)



@app.route('/search_maids', methods=['GET'])
def search_maids():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, street_name FROM streets")
    streets = cur.fetchall()
    cur.close()

    street_id = request.args.get('street')
    maids = []

    if street_id:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM maids WHERE street_id = %s", (street_id,))
        maids = cur.fetchall()
        cur.close()

    return render_template('search_maids.html', streets=streets, maids=maids)


@app.route('/user_dashboard')
def user_dashboard():
    user_id = session.get('user_id')

    # Check if the user is logged in
    if not user_id:
        flash('You need to log in first!', 'danger')
        return redirect(url_for('login'))

    # Fetch the user's details
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()
        cur.close()

        if user is None:
            flash('User not found.', 'danger')
            return redirect(url_for('login'))

    except Exception as e:
        flash(f'Error fetching user: {str(e)}', 'danger')
        return redirect(url_for('login'))

    # Fetch the list of streets
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, street_name FROM streets")
        streets = cur.fetchall()
        cur.close()

    except Exception as e:
        streets = []
        flash(f'Error fetching streets: {str(e)}', 'danger')

    return render_template('user_dashboard.html', user=user, streets=streets)



@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('admin_dashboard.html')


@app.route('/my_grievances')
def my_grievances():
    if 'user_id' not in session:
        flash('You need to log in first.', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT id, title, description, status, created_at 
        FROM grievances 
        WHERE user_id = %s
    """, (user_id,))
    grievances = cur.fetchall()
    cur.close()

    return render_template('my_grievances.html', grievances=grievances)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/add_shop', methods=['GET', 'POST'])
def add_shop():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        street_id = request.form.get('street_id')
        shop_map_url = request.form['shop_map_url']

        shop_image = None
        if 'shop_image' in request.files:
            file = request.files['shop_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                shop_image = filename 

        if not street_id or street_id == '':
            flash('Please select a valid street.', 'error')
            return redirect(url_for('add_shop'))

        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO shops 
                (name, category, street_id, street_name, shop_image, shop_map_url) 
                VALUES (%s, %s, %s, (SELECT street_name FROM streets WHERE id = %s), %s, %s)
            """, (name, category, street_id, street_id, shop_image, shop_map_url))

            mysql.connection.commit()
            cur.close()

            flash('Shop added successfully!', 'success')
            return redirect(url_for('manage_shops'))

        except Exception as e:
            print(f"Error: {e}")
            mysql.connection.rollback()
            flash(f"Error adding shop: {str(e)}", 'error')

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM streets")
    streets = cur.fetchall()
    cur.close()

    return render_template('add_shop.html', streets=streets)



if __name__ == '__main__':
    app.run(host='192.168.1.15', port=5000, debug=True)
