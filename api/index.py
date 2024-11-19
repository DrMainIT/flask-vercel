import flask  
from flask import request,render_template,jsonify,redirect
import sqlite3

app = flask.Flask(__name__)

#database connection local connection

def get_db_connection():
    conn = sqlite3.connect('mydatabase.db')
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
        return redirect('/dashboard')
    else:
        return render_template('login.html')

@app.post('/add')
def createUser():
    data = request.form['username']
    print(data)
    conn = get_db_connection()
    conn.execute('INSERT INTO users (name) VALUES (?)', (data,))
    conn.commit()
    cursor = conn.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    processed_data = []
    for i in users:
        processed_data.append(i[0])
    return render_template('createUser.html', users=processed_data)

@app.get('/showList')
def showUsers():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    processed_data = []
    for i in users:
        processed_data.append(i[0])

    # Create a simple HTML response
    response = "<h2>Submitted Data:</h2><ul>"
    for user in processed_data:
        response += "<li>{}</li>".format(user)
    response += "</ul>"
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)