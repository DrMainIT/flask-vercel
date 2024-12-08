import flask  
from flask import request,render_template,jsonify,redirect
import sqlite3
import shutil
import os

app = flask.Flask(__name__)



# use a database in local 
db_path = os.getenv('DB_PATH', 'mydatabase.db')
def create_tables():
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            money INTEGER NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT,
            description TEXT,
            price INTEGER NOT NULL
        )
    ''')
    products = [
        ("Product 1", "agenda", "This is product 1", 100),
        ("Product 2", "calzini", "This is product 2", 200),
        ("Product 3", "cuscino", "This is product 3", 300)
    ]
    conn.executemany('INSERT INTO products (name, image, description, price) VALUES (?, ?, ?, ?)', products)
    conn.commit()
    conn.close()

create_tables()

def get_db_connection():
    conn = sqlite3.connect(db_path)
    print("Opened database successfully")
    return conn

@app.get('/')
def index():
    return render_template('index.html')

@app.get('/register')
def register():
    return render_template('register.html')

@app.get('/dashboard')
def dashboard():
    id_user = request.args.get('id_user')
    return render_template('dashboard.html',id_user=id_user)

@app.post('/register')
def register_post():
    data = request.form
    #sanitizing the data
    name = data['username']
    email = data['email']
    money = 1000
    password = data['password']
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name,email,password,money) VALUES (?,?,?,?)', (name,email,password,money))
    conn.commit()
    conn.close()
    return render_template('login.html')    

@app.get('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def login_post():
    data = request.form
    email = data['email']
    password = data['password']
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email,password))
    users = cursor.fetchall()
    conn.close()
    if len(users) > 0:
        return redirect(f'/showProducts/{users[0][0]}')
    else:
        return render_template('login.html')

@app.get('/online')
def online():
    id_user = request.args.get('id_user')   
    return render_template('online.html',id_user=id_user)

@app.get('/tutorial')
def tutorial():
    id_user = request.args.get('id_user')   
    return render_template('tutorial.html',id_user=id_user)

@app.get('/showProducts/<int:id_user>')
def showProducts(id_user):
    conn = get_db_connection()
    # recupera tutti i prodotti
    cursor = conn.execute('SELECT * FROM products')
    products = cursor.fetchall()
    # recupera il denaro dell'utente
    cursor2 = conn.execute('SELECT money FROM users WHERE id = (?)', (id_user,))
    money = cursor2.fetchall()
    conn.close()
    # processa i dati
    processed_data = []
    for product in products:
        processed_data.append({
            "id": product[0],
            "name": product[1],
            "link": "img/"+ product[2] + '.webp' if product[2] else "img/default.jpg",
            "description": product[3]
        })
    # Create a simple HTML response
    return render_template('showProducts.html', products=processed_data,money=money[0][0],id_user=id_user)

@app.get('/showProduct/<int:id>')
def showProduct(id):
    id_user = request.args.get('id_user')
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM products WHERE id = ?', (id,))
    product = cursor.fetchone()
    conn.close()
    processed_data = {
        "id": product[0],
        "name": product[1],
        "link": "img/"+ product[2] + '.webp' if product[2] else "img/default.jpg",
        "description": product[3],
        "price": product[4],
    }
    return render_template('showProduct.html', product=processed_data,id_user=id_user)

@app.get('/confirm-purchase')
def confirm_purchase():
    id_user = request.args.get('id_user')
    id_product = request.args.get('id_product')

    # update the money of the user 
    conn = get_db_connection()
    cursor = conn.execute('SELECT price FROM products WHERE id = ?', (id_product,))
    price = cursor.fetchone()
    cursor2 = conn.execute('SELECT money FROM users WHERE id = ?', (id_user,))
    money = cursor2.fetchone()
    new_money = money[0] - price[0]
    conn.execute('UPDATE users SET money = ? WHERE id = ?', (new_money,id_user))
    conn.commit()
    conn.close()
    return render_template('confirm-purchase.html',id_user=id_user)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)