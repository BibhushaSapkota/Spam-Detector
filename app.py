import mysql.connector
from flask import Flask, render_template, request, redirect, session, url_for
import joblib
import os
import re

app = Flask(__name__)
app.secret_key = 'abc'

model = joblib.load('spam_model.pkl')

@app.route('/index',methods=['GET', 'POST'])

def index():
  if request.method == 'POST':
    message = request.form.get('message')
    output = model.predict([message])
    if output == [0]:
      result = "This Message is Not a SPAM Message."
    else:
      result = "This Message is a SPAM Message." 
    return render_template('index.html', result=result,message=message)      

  else:
    return render_template('index.html')

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/register',methods=['GET', 'POST'])
def register():
  mydb=mysql.connector.Connect(
    host="localhost",
    port=3307,
    user="root",
    password="",
    database="spam"
  )
  cursor=mydb.cursor()
  msg = ''
  if request.method == 'POST' and 'Name' in request.form and 'Password' in request.form and 'Email' in request.form and 'CPassword' in request.form:
      name = request.form['Name']
      password = request.form['Password']
      email = request.form['Email']
      cpassword=request.form['CPassword']

      cursor.execute('SELECT * FROM register WHERE Name = %s', [name])
      account = cursor.fetchone()
      if account:
          msg = 'Account already exists !'
      elif not name or not password or not email or not cpassword:
          msg = 'Please fill out the form !'
      elif not re.match(r'[A-Za-z0-9]+', name):
          msg = 'Username must contain only characters and numbers !'
      elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
          msg = 'Invalid email address !'
      elif password<=7:
          msg="Password must be atleast 8 letters"
      elif password!=cpassword:
          msg='Password and confirm password doesnt match'
      else:
          cursor.execute('''INSERT INTO register VALUES(NULL,%s, %s, %s)''', (name,email,password,))
          mydb.commit()
          return render_template('login.html')
  elif request.method == 'POST':
      msg = 'Please fill out the form !'
  return render_template('signup.html', msg=msg)

@app.route('/login', methods =['GET', 'POST'])
def login():
    mydb = mysql.connector.Connect(
        host="localhost",
        port=3307,
        user="root",
        password="",
        database="spam"
    )
    cursor = mydb.cursor()
    msg = ''
    if request.method == 'POST' and 'Name' in request.form and 'Password' in request.form:
        Name = request.form['Name']
        Password = request.form['Password']
        cursor.execute('''SELECT * FROM register WHERE Name = %s AND Password = %s''', [Name, Password])
        user= cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['Username'] = Name
            return render_template('home.html')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('Username', None)
    return redirect (url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT",5000))
    app.run(debug=True,host='0.0.0.0',port=5000)
