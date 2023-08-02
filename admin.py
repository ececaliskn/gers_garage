from flask import Flask, render_template, request, redirect, url_for, jsonify
import secrets
import MySQLdb
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True

# MySQL yapılandırması
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gersgarage'

# Veritabanı bağlantısını oluştur
mysql = MySQLdb.connect(
    host=app.config['MYSQL_HOST'],
    user=app.config['MYSQL_USER'],
    passwd=app.config['MYSQL_PASSWORD'],
    db=app.config['MYSQL_DB']
)

# Function to create and return a database connection
def get_database_connection():
    return mysql

@app.route('/view_schedule', methods=['POST'])
def view_schedule():
    data = request.get_json()
    date = data.get('date')

    if date:
        # Get database connection
        connection = get_database_connection()
        cursor = connection.cursor()

        # Retrieve bookings for the selected date with customer, vehicle, and service details
        query = """
            SELECT b.booking_id, c.name, c.surname, v.vehicle_type, v.make, s.service_type
            FROM bookings b
            INNER JOIN customers c ON b.customer_id = c.customer_id
            INNER JOIN vehicles v ON b.vehicle_id = v.vehicle_id
            INNER JOIN services s ON b.service_id = s.service_id
            WHERE b.booking_date = %s
        """
        cursor.execute(query, (date,))
        booking_details = cursor.fetchall()

        cursor.close()
        connection.close()

        return jsonify({'date': date, 'booking_details': booking_details})
    
    return jsonify({'date': None, 'booking_details': None})

# allocate_mechanic işlevi
@app.route('/allocate_mechanic', methods=['POST'])
def allocate_mechanic():
    booking_id = request.form['booking_id']
    mechanic_name = request.form['mechanic_name']

    # Rezervasyonu güncelle ve mekanik atamayı kaydet
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE bookings SET mechanic_name = %s WHERE booking_id = %s", (mechanic_name, booking_id))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('view_schedule'))




































@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect to the login page when first accessing the website

@app.route('/admin_index.html')
def admin_index1():
    
    return render_template('admin_index.html')

@app.route('/admin_invoice.html')
def admin_invoice1():
    return render_template('admin_invoice.html')


@app.route('/admin_schedule.html')
def admin_schedule1():
    return render_template('admin_schedule.html')



@app.route('/admin_index', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = validate_user(username, password)
        if user:
            # Kullanıcı adı ve şifre doğru, giriş başarılı, ana sayfaya yönlendir
            session['user_id'] = user[0]  # User ID'yi session'a kaydet
            return redirect('/admin_index.html')  # Redirect to admin_index.html after successful login
        else:
            # Kullanıcı adı veya şifre yanlış, hata mesajıyla tekrar login sayfasına dön
            error_message = "Invalid username or password"
            return render_template('admin_login.html', error_message=error_message)

    # For GET requests, render the login page
    return render_template('admin_login.html')

# Kullanıcı adı ve şifreyi doğrula
def validate_user(username, password):
    cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    return user

@app.route('/logout')
def logout():
    # Kullanıcıyı çıkış yaparken session'dan sil
    session.pop('user_id', None)
    return redirect(url_for('login'))


@app.route('/admin_index')
def admin_index():
    # Check if the user is logged in
    if 'user_id' in session:
        return render_template('admin_index.html')
    else:
        # User is not logged in, redirect to the login page
        return redirect('/admin_login.html') 
if __name__ == "__main__":
    app.run(debug=True)
