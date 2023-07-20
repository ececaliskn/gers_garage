from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
import secrets




 

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True

# MySQL yapılandırması
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gersgarage'


mysql = MySQL(app)



@app.route('/login.html')
def login1():
    return render_template('login.html')


@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/booking.html')
def booking():
    return render_template('booking.html')


@app.route('/contact.html')
def contact():
    return render_template('contact.html')


@app.route('/prices.html')
def price():
    return render_template('prices.html')


@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/service.html')
def service():
    return render_template('service.html')


@app.route('/register.html')
def register():
    return render_template('register.html')




@app.route('/')
def home():
    # Kullanıcı oturumunu kontrol et
    if 'user_id' in session:
        return redirect('/myprofile.html')

    return redirect('/login.html')


@app.route('/add_user', methods=["POST"])
def add_user():
    # Formdan verileri al
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    email = request.form['email']
    password1 = request.form['password1']
    password2 = request.form['password2']
    username = request.form['username']
    phone = request.form['phone']

    # Boş alan kontrolü yap
    if not firstName or not lastName or not email or not password1 or not password2 or not username or not phone:
        message = "Please fill in all fields"
        return render_template('register.html', message=message, firstName=firstName, lastName=lastName, email=email,
                               username=username, phone=phone)

    # Şifrelerin eşleşip eşleşmediğini kontrol et
    if password1 != password2:
        message = "Passwords do not match. Please try again."
        return render_template('register.html', message=message, firstName=firstName, lastName=lastName, email=email,
                               username=username, phone=phone)

    # E-posta adresinin önceden kaydedilip kaydedilmediğini kontrol et
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
    existing_email = cursor.fetchone()
    cursor.close()

    if existing_email:
        message = "This email is already registered. Please use a different email address."
        return render_template('register.html', message=message, firstName=firstName, lastName=lastName, email=email,
                               username=username, phone=phone)

    # Kullanıcı adının önceden kaydedilip kaydedilmediğini kontrol et
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM customers WHERE username = %s", (username,))
    existing_username = cursor.fetchone()
    cursor.close()

    if existing_username:
        message = "This username is already taken. Please choose a different username."
        return render_template('register.html', message=message, firstName=firstName, lastName=lastName, email=email,
                               username=username, phone=phone)

    # MySQL cursor oluştur
    cur = mysql.connection.cursor()

    # Veritabanına ekleme sorgusu
    cur.execute("INSERT INTO customers(customer_id, name, surname, email, password, username, mobile_phone) VALUES (NULL, %s, %s, %s, %s, %s, %s)",
                (firstName, lastName, email, password1, username, phone))

    # Değişiklikleri kaydet ve cursor'u kapat
    mysql.connection.commit()
    cur.close()

    # Başarılı kayıt mesajı
    message = "Registration successful! Please login."
    return redirect('/login?message=' + message)


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # E-posta adresine ait kullanıcıyı veritabanından getir
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and user[4] == password:

            session['user_id'] = user[0]
            session.permanent = True
            return redirect('/myprofile.html')
        else:
            message = "Incorrect email or password. Please try again."
            return render_template('login.html', message=message)

    message = request.args.get('message')
    return render_template('login.html', message=message)


@app.route('/myprofile.html')
def myprofile():
    # Kullanıcı oturumunu kontrol et
    if 'user_id' in session:

        print(session)
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM customers WHERE customer_id = %s", (user_id,))
        user = cursor.fetchone()
        print(user)
        cursor.close()

        if user:
            email = user[3]
            mobile_phone = user[2]

            return render_template('myprofile.html', email=email, mobile_phone=mobile_phone)

    return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login.html')


if __name__ == "__main__":
    app.run(debug=True)
