import flask  
from flask import request,render_template,jsonify,redirect
import sqlite3
import shutil
import os

app = flask.Flask(__name__)

#database connection local connection
# Copy the database to a writable location
db_path = './mydatabase.db'  # Path in the deployed source
temp_db_path = '/tmp/mydatabase.db'

if not os.path.exists(temp_db_path):
    print("Copying database")
    shutil.copy(db_path, temp_db_path)

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
    return render_template('dashboard.html')

@app.post('/register')
def register_post():
    data = request.form
    #sanitizing the data
    name = data['username']
    email = data['email']
    password = data['password']
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name,email,password) VALUES (?,?,?)', (name,email,password))
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
        return redirect('/showProducts')
    else:
        return render_template('login.html')

@app.get('/online')
def online():
    return render_template('online.html')

@app.get('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.get('/showProducts')
def showProducts():
    conn = get_db_connection()
    # create a table
    cursor = conn.execute('SELECT * FROM products')
    products = cursor.fetchall()
    conn.close()
    processed_data = []
    for product in products:
        print(product[2])
        processed_data.append({
            "id": product[0],
            "name": product[1],
            "link": "img/"+ product[2] + '.webp' if product[2] else "img/default.jpg",
            "description": product[3]
        })
    # Create a simple HTML response
    return render_template('showProducts.html', products=processed_data)

@app.get('/showProduct/<int:id>')
def showProduct(id):
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
    return render_template('showProduct.html', product=processed_data)

@app.get('/confirm-purchase')
def confirm_purchase():
    return render_template('confirm-purchase.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)